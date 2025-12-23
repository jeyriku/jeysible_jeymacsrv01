employees = [
    {'name': 'Tanya', 'age': 20, 'birthday': '1990-03-10',
        'job': 'Back-end Engineer', 'address': {'city': 'New York', 'country': 'USA'}},
    {'name': 'Tim', 'age': 35, 'birthday': '1985-02-21', 'job': 'Developer', 'address': {'city': 'Sydney', 'country': 'Australia'}}]


for employee in employees:
    print(f"{employee['name']}, {employee['job']}, {employee['address']['city']}")
