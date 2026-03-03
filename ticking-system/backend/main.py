from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import boto3
from boto3.dynamodb.conditions import Key
import schemas, auth, keyword_model
import os
import uuid
from datetime import datetime

app = FastAPI(title="Cloud Support Ticket Classification API (Serverless)")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB Setup
REGION = os.environ.get("REGION", "us-east-1")
TICKETS_TABLE_NAME = os.environ.get("TICKETS_TABLE_NAME", "TicketsTable")
USERS_TABLE_NAME = os.environ.get("USERS_TABLE_NAME", "UsersTable")

# Initialize boto3 resource. In Lambda, it picks up execution role implicitly.
# If running locally, you must have AWS credentials configured.
dynamodb = boto3.resource('dynamodb', region_name=REGION)
tickets_table = dynamodb.Table(TICKETS_TABLE_NAME)
users_table = dynamodb.Table(USERS_TABLE_NAME)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except auth.jwt.JWTError:
        raise credentials_exception
        
    response = users_table.get_item(Key={'username': username})
    user = response.get('Item')
    if not user:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@app.on_event("startup")
def startup_event():
    # Attempt to create default admin (DynamoDB will overwrite if exists, but we can do a quick check)
    try:
        response = users_table.get_item(Key={'username': 'admin'})
        if 'Item' not in response:
            users_table.put_item(Item={
                'username': 'admin',
                'password_hash': auth.get_password_hash("admin123"),
                'is_admin': True,
                'id': str(uuid.uuid4())
            })
    except Exception as e:
        print(f"Startup DB check failed (this is normal if table isn't created yet or credentials aren't set locally): {e}")


@app.post("/api/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate):
    response = users_table.get_item(Key={'username': user.username})
    if 'Item' in response:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_password = auth.get_password_hash(user.password)
    new_user = {
        'username': user.username,
        'password_hash': hashed_password,
        'is_admin': False,
        'id': str(uuid.uuid4())
    }
    users_table.put_item(Item=new_user)
    
    return schemas.UserResponse(
        username=new_user['username'],
        id=hash(new_user['id']), # Schemas expects int, Dynamo uses string hash
        is_admin=new_user['is_admin']
    )

@app.post("/api/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    response = users_table.get_item(Key={'username': form_data.username})
    user = response.get('Item')
    
    if not user or not auth.verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/tickets/", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, current_user: dict = Depends(get_current_user)):
    user_id_str = str(current_user.get('id', ''))
    
    # Check for duplicates using a Scan (Scanning DynamoDB isn't ideal for scaling, 
    # but works for this demo. Ideally, a GSI on user_id would be better.)
    response = tickets_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_id').eq(user_id_str) & 
                         boto3.dynamodb.conditions.Attr('title').eq(ticket.title) &
                         boto3.dynamodb.conditions.Attr('description').eq(ticket.description)
    )
    
    if response.get('Items'):
        raise HTTPException(status_code=400, detail="Ticket already exists. Please change your input.")

    # Classify ticket
    predicted_category = keyword_model.classify_ticket(ticket.title, ticket.description)
    
    # Create DB record
    ticket_id = str(uuid.uuid4())
    now_iso = datetime.utcnow().isoformat()
    
    db_ticket = {
        'id': ticket_id,
        'title': ticket.title,
        'description': ticket.description,
        'category': predicted_category,
        'user_id': user_id_str,
        'created_at': now_iso
    }
    tickets_table.put_item(Item=db_ticket)
    
    # Generate response
    return schemas.TicketResponse(
        id=hash(ticket_id), # schemas expects int
        title=db_ticket['title'],
        description=db_ticket['description'],
        category=db_ticket['category'],
        user_id=hash(user_id_str),
        created_at=datetime.fromisoformat(now_iso)
    )

@app.get("/api/tickets/", response_model=list[schemas.TicketResponse])
def get_tickets(current_user: dict = Depends(get_current_user)):
    user_id_str = str(current_user.get('id', ''))
    # Scan for user's tickets 
    response = tickets_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_id').eq(user_id_str)
    )
    items = response.get('Items', [])
    
    # Sort locally
    items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return [schemas.TicketResponse(
        id=hash(item['id']),
        title=item['title'],
        description=item['description'],
        category=item['category'],
        user_id=hash(item.get('user_id', '')),
        created_at=datetime.fromisoformat(item['created_at'])
    ) for item in items]

@app.get("/api/admin/tickets/", response_model=list[schemas.TicketResponse])
def get_all_tickets_admin(current_user: dict = Depends(get_current_admin_user)):
    response = tickets_table.scan()
    items = response.get('Items', [])
    
    # Sort locally
    items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return [schemas.TicketResponse(
        id=hash(item['id']),
        title=item['title'],
        description=item['description'],
        category=item['category'],
        user_id=hash(item.get('user_id', '')),
        created_at=datetime.fromisoformat(item['created_at'])
    ) for item in items]

# Wrap FastAPI app with Mangum for AWS Lambda
handler = Mangum(app)
