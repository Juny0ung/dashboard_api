# Elice Backend Team Interview Project: 게시판 API
사용자가 게시판에 글을 올릴 수 있는 API이다. 사용자는 이메일을 통해서 회원가입을 하고 로그인을 할 수 있고, 공개 여부를 선택해서 게시판을 만들 수 있다. 그리고 본인의 게시판 혹은 공개된 게시판에 글을 올릴 수 있다.


## Project setup
```
pip install -r requirements.txt
```

## Run
```
docker-compose up
python uvicorn app.main ~~
```

## Database
API를 구현하기 위해 세 개의 database table을 만들었다. 

- users : 사용자의 정보를 가진 table이다.
  
| Property Name | Type | Content |
| --------| ---- | ---- |
| id | Integer | 사용자 id |
| fullname | String | 사용자 이름 |
| email | String | 사용자 이메일 |
| hashpassword | String | 암호화된 사용자 비밀번호 |
| salt | String | 사용자 비밀번호를 암호화하기 위한 변수 |

- dashboards : 게시판의 정보를 가진 table이다.

| Property Name | Type | Content |
| --------| ---- | ---- |
| id | Integer | 게시판 id |
| name | String | 게시판 이름 |
| public | Boolean | 공개 여부 |
| posts_cnt | Integer | 가지고 있는 게시글 수 |
| creator_id | Integer | 게시판 생성자 id |

- posts : 게시글의 정보를 가진 table이다.

| Property Name | Type | Content |
| --------| ---- | ---- |
| id | Integer | 게시글 id |
| title | String | 게시글 제목 |
| content | String | 공개 여부 |
| writer_id | Integer | 작성자 id |
| dashboard_id | Integer | 게시글이 있는 게시판 id |






## API

### 회원 가입
사용자를 추가한다. 이름, 이메일, 비밀번호를 통해서 사용자를 추가한다. 이때, 비밀번호는 암호화해서 DB에 저장된다.
#### Request

`POST /user/signup`

```json
"body": {
  "fullname": "String",
  "email": "String",
  "password": "String"
}
```

### 로그인
이메일, 비밀번호로 로그인한다. header를 통해서 access-token을 받는다. access-token은 jwt를 활용했고 보안을 위해 payload에 random 값을 추가했다.
#### Request
`POST /user/login`
```json
"body": {
  "email": "String",
  "password": "String"
}
```
#### Response
```json
"header": {
  "access-token": "String"
}
```

### 로그아웃
access-token을 통해서 로그아웃한다. 
#### Request
`POST /user/logout`
```json
"header": {
  "access-token": "String"
}
```

### 게시판 만들기
게시판의 이름과 공개 여부를 통해서 게시판을 만든다. access-token을 통해서 생성자를 확인한다.
#### Request
`POST /dashboard/create`
```json
"header": {
  "access-token": "String"
},
"body": {
  "name": "String",
  "public": "Boolean"
}
```

### 게시판 업데이트 하기
게시판의 id로 게시판의 이름과 공개 여부를 수정한다. 본인이 만든 게시판만 수정할 수 있다.
#### Request
`PUT /dashboard/update`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
},
"body": {
  "name": "String",
  "public": "Boolean"
}
```

### 게시판 삭제하기
게시판의 id로 게시판을 삭제한다. 본인이 만든 게시판만 삭제할 수 있다.
#### Request
`POST /dashboard/delete`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
}
```

### 게시판 조회하기
게시판의 id를 통해서 게시판을 조회한다. 공개되었거나 본인이 만들어서 본인이 확인할 수 있는 게시판만 조회할 수 있다.
#### Request
`GET \dashboard\get`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
}
```
#### Response
```json
"body": {
  "id": "Integer",
  "name": "String",
  "public": "Boolean",
  "creator_id": "Integer"
}
```

### 게시판 list 조회하기
본인이 조회할 수 있는 게시판의 list를 조회한다. `is_sort`가 0이면 id 순으로 조회하고 1이면 가지고 있는 게시글 순으로 조회한다. `pgsize`개의 게시판을 조회하는데 이전 조회의 마지막 게시판의 `id`나 `posts_cnt`를 통해 다음 `pgsize`개의 게시글을 효율적으로 조회한다.
#### Request
`GET \dashboard\list`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "pgsize": "Integer"
}
"body": {
  "is_sort": "Integer",
  "id": "Integer",
  "posts_cnt": "Integer"
}
```
#### Response
```json
"body": {
  "result": [
    {
      "id": "Integer",
      "name": "String",
      "public": "Boolean",
      "creator_id": "Integer"
    }
  ],
  "current_cursor": {
    "is_sort": "Integer",
    "id": "Integer",
    "posts_cnt": "Integer"
  }
  "next_cursor": {
    "is_sort": "Integer",
    "id": "Integer",
    "posts_cnt": "Integer"
  }
} 
```

### 게시글 작성하기
본인이 조회할 수 있는 게시판에 게시글을 작성한다.
#### Request
`POST \post\create`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
},
"body": {
  "title": "String",
  "content": "String"
}
```

### 게시글 수정하기
본인이 작성한 게시글을 수정한다.
#### Request
`POST \post\update`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
},
"body": {
  "title": "String",
  "content": "String"
}
```

### 게시글 삭제하기
본인이 작성한 게시글을 삭제한다.
#### Request
`POST \post\delete`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
}
```

### 게시글 조회하기
게시글 id를 통해 본인이 조회할 수 있는 게시판에 있는 게시글을 조회한다.
#### Request
`POST \post\get`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
}
```
#### Response
```json
"body": {
  "id": "Integer",
  "title": "String",
  "content": "String",
  "writer_id": "Integer",
  "dashboard_id": "Integer"
}
```

### 게시글 list 조회하기
게시판 id를 통해 본인이 게시판에 있는 게시글 list를 조회한다. `pgsize`개의 게시글을 조회하는데 이전 조회의 마지막 게시글의 `id`를 통해 다음 `pgsize`개의 게시글을 효율적으로 조회한다.
#### Request
`POST \post\list`
```json
"header": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer",
  "pgsize": "Integer"
},
"body": {
  "is_sort": "Integer",
  "id": "Integer"
}
```
#### Response
```json
"body": {
  "result": [
    "body": {
      "id": "Integer",
      "title": "String",
      "content": "String",
      "writer_id": "Integer",
      "dashboard_id": "Integer"
    }
  ],
  "current_cursor": {
    "is_sort": "Integer",
    "id": "Integer"
  }
  "next_cursor": {
    "is_sort": "Integer" = 0,
    "id": "Integer"
  }
}
```
