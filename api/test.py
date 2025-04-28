from requests import get, post, delete

# print(get('http://localhost:8000/api/oil').json())
#
# print(get('http://localhost:5000/api/oil/52').json())
#
# print(post('http://localhost:5000/api/oil',
# json={'title': 'Заголовок',
# 'coo': 'n.txt'}).json())
#
# print(delete('http://localhost:5000/api/oil/5').json())
#
# print(post('http://localhost:5000/api/oil/22',
# json={'title': 'Заголовок12',
# 'coo': '198378193'}).json())
#
# print(get('http://localhost:5000/api/oil/load/31',
# json={'title': 'Заголовок12',
# 'coo': '12322'}).json())


print(get('http://localhost:8000/api/user/4').json())
#
# print(post('http://localhost:5000/api/users',
# json={'name': 'Admin',
# 'email': 'admin@mail.ru',
# 'password': 'admin',
# 'right_id': 1}).json())

# print(post('http://localhost:5000/api/rights',
# json={'name': 'someone'}).json())
