
print("""{
  "fps": 60,
  "events": [
""")
for i in range(15,140+15,2):
    print('''
      {
        "frame": '''+f"{i}"+''',
        "key": "LEFT",
        "action": "down"
      },
      {
        "frame": '''+f"{i+1}"+''',
        "key": "LEFT",
        "action": "up"
      }''',end=",")
for i in range(200,140+200,2):
    print('''
      {
        "frame": '''+f"{i}"+''',
        "key": "RIGHT",
        "action": "down"
      },
      {
        "frame": '''+f"{i+1}"+''',
        "key": "RIGHT",
        "action": "up"
      }''',end="," if i < 140+200-2 else "")
print("""
  ]
}
""")
