# 게시판 API
사용자가 게시판에 글을 올릴 수 있는 API이다. 사용자는 이메일을 통해서 회원가입을 하고 로그인을 할 수 있고, 공개 여부를 선택해서 게시판을 만들 수 있다. 그리고 본인의 게시판 혹은 공개된 게시판에 글을 올릴 수 있다. Python 3.10을 통해서 구현되었다.


## Project setup
```
pip install -r requirements.txt
```

## Run
```
docker-compose up
python -m uvicorn app.main:app --reload
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
사용자를 추가한다. 이름, 이메일, 비밀번호를 통해서 사용자를 추가한다. 이때, 비밀번호는 암호화해서 DB에 저장된다. 암호화를 위해서 사용자별로 random한 문자열을 생성해서 salt로 붙이고 SHA-256으로 hashing했다.
#### Request

`POST /user`

```json
"body": {
  "fullname": "String",
  "email": "String",
  "password": "String"
}
```

#### Response
```json
"body": {
  "id": "Integer"
  "fullname": "String",
  "email": "String"
}
```

### 로그인
이메일, 비밀번호로 로그인한다. headers를 통해서 access-token을 받는다. access-token은 jwt를 활용했고 보안을 위해 payload에 random 값을 추가했다.
#### Request
`POST /user/login`
```json
"body": {
  "id": "Integer"
  "email": "String",
  "password": "String"
}
```
#### Response
```json
"headers": {
  "access-token": "String"
}
```

### 로그아웃
access-token을 통해서 로그아웃한다. 
#### Request
`POST /user/logout`
```json
"headers": {
  "access-token": "String"
}
```

#### Response
```json
"body": {
  "id": "Integer"
}
```

### 게시판 만들기
게시판의 이름과 공개 여부를 통해서 게시판을 만든다. access-token을 통해서 생성자를 확인한다.
#### Request
`POST /dashboard`
```json
"headers": {
  "access-token": "String"
},
"body": {
  "name": "String",
  "public": "Boolean"
}
```
#### Response
```json
"body": {
  "id": "Integer"
  "name": "String",
  "public": "Boolean",
  "creator_id": "Integer",
  "posts_cnt": "Integer"
}
```

### 게시판 업데이트 하기
게시판의 id로 게시판의 이름과 공개 여부를 수정한다. 본인이 만든 게시판만 수정할 수 있다.
#### Request
`PUT /dashboard`
```json
"headers": {
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

#### Response
```json
"body": {
  "id": "Integer"
  "name": "String",
  "public": "Boolean",
  "creator_id": "Integer",
  "posts_cnt": "Integer"
}
```

### 게시판 삭제하기
게시판의 id로 게시판을 삭제한다. 본인이 만든 게시판만 삭제할 수 있다.
#### Request
`DELETE /dashboard`
```json
"headers": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
}
```

#### Response
```json
"body": {
  "id": "Integer"
  "name": "String",
  "public": "Boolean",
  "creator_id": "Integer",
  "posts_cnt": "Integer"
}
```

### 게시판 조회하기
게시판의 id를 통해서 게시판을 조회한다. 공개되었거나 본인이 만들어서 본인이 확인할 수 있는 게시판만 조회할 수 있다.
#### Request
`GET \dashboard`
```json
"headers": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
}
```
#### Response
```json
"body": {
  "id": "Integer"
  "name": "String",
  "public": "Boolean",
  "creator_id": "Integer",
  "posts_cnt": "integer"
}
```

### 게시판 list 조회하기
본인이 조회할 수 있는 게시판의 list를 조회한다. `cursor`의 값에 따라 id 순이나 게시글 순으로 조회한다. `pgsize`개의 게시판을 조회하는데 이전 조회의 마지막 게시판의 `id`나 `posts_cnt` 값을 `next_cursor`를 통해 전달 받아 다음 `pgsize`개의 게시글을 효율적으로 조회한다.

초기에 `cursor`값을 전달하지 않으면 id 순으로 `pgsize` 게시판을 조회한다. `cursor`값을 `1`로 전달하면 게시글 수 순으로 `pgsize` 게시판을 조회한다. 이후에는 response로 받은 `next_cursor`를 `cursor`에 parameter로 넣어서 전달하면 그 다음 `pgsize` 게시글을 반환한다. `cursor`는 id 순 정렬일 경우 `0_{id}`, 게시글 수 순 정렬일 경우 `1_{posts_cnt}_{id}`의 형태를 갖는다. 이전 `pgsize` 게시글을 조회하는데 활용하기 위해 `current_cursor`에 현재 `cursor`를 저장해 반환한다. `pgsize`의 default 값은 10이다.
#### Request
`GET \dashboard\list`
```json
"headers": {
  "access-token": "String"
},
"parameters": {
  "pgsize": "Integer",
  "cursor": "String"
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
  "current_cursor": "String"
  "next_cursor": "String"
} 
```

### 게시글 작성하기
본인이 조회할 수 있는 게시판에 게시글을 작성한다.
#### Request
`POST \post`
```json
"headers": {
  "access-token": "String"
},
"parameters": {
  "dashid": "Integer"
},
"body": {
  "title": "String",
  "content": "String"
}
```
#### Response
```json
"body": {
  "id": "Integer"
  "title": "String",
  "content": "String",
  "writer_id": "Integer",
  "dashboard_id": "Integer"
}
```

### 게시글 수정하기
본인이 작성한 게시글을 수정한다.
#### Request
`PUT \post`
```json
"headers": {
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
#### Response
```json
"body": {
  "id": "Integer"
  "title": "String",
  "content": "String",
  "writer_id": "Integer",
  "dashboard_id": "Integer"
}
```

### 게시글 삭제하기
본인이 작성한 게시글을 삭제한다.
#### Request
`DELETE \post`
```json
"headers": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
}
```
#### Response
```json
"body": {
  "id": "Integer"
  "title": "String",
  "content": "String",
  "writer_id": "Integer",
  "dashboard_id": "Integer"
}
```

### 게시글 조회하기
게시글 id를 통해 본인이 조회할 수 있는 게시판에 있는 게시글을 조회한다.
#### Request
`GET \post`
```json
"headers": {
  "access-token": "String"
},
"parameters": {
  "id": "Integer"
}
```
#### Response
```json
"body": {
  "id": "Integer"
  "title": "String",
  "content": "String",
  "writer_id": "Integer",
  "dashboard_id": "Integer"
}
```

### 게시글 list 조회하기
게시판 id를 통해 본인이 게시판에 있는 게시글 list를 조회한다. `pgsize` 게시글을 조회하는데 이전 조회의 마지막 게시글의 `id`를 `next_cursor`에 전달 받아 다음 `pgsize` 게시글을 효율적으로 조회한다. 초기에는 `cursor` 값을 전달하지 않아도 `pgsize` 게시글을 반환한다. 이후에는 response로 받은 `next_cursor`를 `cursor` parameter로 넣어서 전달하면 그 다음 `pgsize` 게시글을 반환한다. 이전 `pgsize` 게시글을 조회하는데 활용하기 위해 `current_cursor`에 현재 `cursor`를 저장해 반환한다. `pgsize`의 default 값은 10이다.
#### Request
`GET \post\list`
```json
"headers": {
  "access-token": "String"
},
"parameters": {
  "dashid": "Integer",
  "pgsize": "Integer",
  "cursor": "String"
}
```
#### Response
```json
"body": {
  "result": [
    {
      "id": "Integer",
      "title": "String",
      "content": "String",
      "writer_id": "Integer",
      "dashboard_id": "Integer"
    }
  ],
  "current_cursor": "String"
  "next_cursor": "String"
}
```
