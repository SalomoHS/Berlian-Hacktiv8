import requests


def task_1():
    user = requests.get("https://jsonplaceholder.typicode.com/users")
    post = requests.get("https://jsonplaceholder.typicode.com/posts")

    print("=" * 10 + "Status Code" + "=" * 10)
    print(f"User: {user.status_code}")
    print(f"Task: {post.status_code}")

    print()
    print("=" * 10 + "Info" + "=" * 10)
    print(f"Jumlah user: {user.status_code}")
    print(f"Jumlah post: {post.status_code}")

    print()
    print("=" * 10 + "Nama & Email 3 User Pertama" + "=" * 10)
    for idx, i in enumerate(user.json()):
        print(f"Nama: {i['name']}")
        print(f"Email: {i['email']}")
        print("=" * 10)
        if idx == 2:
            break

    print()
    print("=" * 10 + "posts_per_user" + "=" * 10)
    posts_per_user = {}
    for i in user.json():
        get_post_by_user_id = [j for j in post.json() if j['userId'] == i['id']]
        posts_per_user[str(i['id'])] = len(get_post_by_user_id)

    print(posts_per_user)
    return user.json(), posts_per_user

def task_2(user, posts_per_user):
    user_summary = []
    temp = {}
    for i in user:
        temp['id'] = i['id']
        temp['nama'] = i['name']
        temp['email'] = i['email']
        temp['kota'] = i['address']['city']
        temp['jumlah_post'] = posts_per_user[str(i['id'])]
        
        user_summary.append(temp)
        temp = {}

    print()
    print("=" * 10 + "User Post Terbanyak" + "=" * 10)
    top_3_post = sorted(user_summary, key=lambda x: x['jumlah_post'], reverse=True)[:3]
    for idx, i in enumerate(top_3_post):
        print(f"{idx + 1}. {i['nama']} ({i['kota']}) — [{i['jumlah_post']}]")

if __name__ == "__main__":
    user, posts_per_user = task_1()
    task_2(user, posts_per_user)