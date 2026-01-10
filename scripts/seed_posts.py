import sys
sys.path.append('..')

from models.post import Post

sample_posts = [
    {
        'post_id': 'post_001',
        'name': 'John Doe',
        'caption': 'Beautiful sunset at the beach! Perfect evening with family. #sunset #beach #nature',
        'media_url': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e',
        'media_type': 'image'
    },
    {
        'post_id': 'post_002',
        'name': 'Sarah Smith',
        'caption': 'New smartphone unboxing! This camera quality is amazing. Best tech purchase of 2024. #tech #smartphone',
        'media_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9',
        'media_type': 'image'
    },
    {
        'post_id': 'post_003',
        'name': 'Mike Johnson',
        'caption': 'Workout complete! Leg day is the hardest but most rewarding. #fitness #gym #motivation',
        'media_url': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48',
        'media_type': 'image'
    },
    {
        'post_id': 'post_004',
        'name': 'Emma Wilson',
        'caption': 'Homemade pizza night! Fresh ingredients make all the difference. Recipe coming soon. #food #cooking',
        'media_url': 'https://images.unsplash.com/photo-1513104890138-7c749659a591',
        'media_type': 'image'
    },
    {
        'post_id': 'post_005',
        'name': 'David Lee',
        'caption': 'Morning coffee and coding session. Building something exciting! #developer #tech #coffee #coding',
        'media_url': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085',
        'media_type': 'image'
    },
    {
        'post_id': 'post_006',
        'name': 'Lisa Brown',
        'caption': 'Makeup tutorial coming soon! This new eyeshadow palette is gorgeous. #beauty #makeup #tutorial',
        'media_url': 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796',
        'media_type': 'image'
    },
    {
        'post_id': 'post_007',
        'name': 'Tom Harris',
        'caption': 'Mountain hiking adventure! The view from the top was breathtaking. #hiking #nature #adventure #mountains',
        'media_url': 'https://images.unsplash.com/photo-1551632811-561732d1e306',
        'media_type': 'image'
    },
    {
        'post_id': 'post_008',
        'name': 'Anna Martinez',
        'caption': 'New book recommendations! Just finished this amazing thriller novel. Page turner! #reading #books #thriller',
        'media_url': 'https://images.unsplash.com/photo-1512820790803-83ca734da794',
        'media_type': 'image'
    },
    {
        'post_id': 'post_009',
        'name': 'Chris Taylor',
        'caption': 'Gaming setup complete! Ready for the weekend gaming marathon. RGB everything! #gaming #setup #tech #rgb',
        'media_url': 'https://images.unsplash.com/photo-1593305841991-05c297ba4575',
        'media_type': 'image'
    },
    {
        'post_id': 'post_010',
        'name': 'Jennifer White',
        'caption': 'Travel diaries: Exploring ancient architecture in Rome. History comes alive here! #travel #rome #architecture',
        'media_url': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5',
        'media_type': 'image'
    },
    {
        'post_id': 'post_011',
        'name': 'Robert Green',
        'caption': 'Yoga session at sunrise. Finding inner peace. #yoga #wellness #meditation #morning',
        'media_url': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773',
        'media_type': 'image'
    },
    {
        'post_id': 'post_012',
        'name': 'Maria Garcia',
        'caption': 'Fashion week ready! New outfit collection. Style is a way to say who you are. #fashion #style #outfit',
        'media_url': 'https://images.unsplash.com/photo-1483985988355-763728e1935b',
        'media_type': 'image'
    },
    {
        'post_id': 'post_013',
        'name': 'Kevin Brown',
        'caption': 'Street photography in Tokyo. Urban life at its finest. #photography #tokyo #urban #street',
        'media_url': 'https://images.unsplash.com/photo-1536098561742-ca998e48cbcc',
        'media_type': 'image'
    },
    {
        'post_id': 'post_014',
        'name': 'Sophie Davis',
        'caption': 'Baking therapy! Fresh croissants from scratch. The smell is heavenly! #baking #croissants #food',
        'media_url': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a',
        'media_type': 'image'
    },
    {
        'post_id': 'post_015',
        'name': 'Alex Turner',
        'caption': 'Music production session. Creating beats late at night. #music #producer #beats #studio',
        'media_url': 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04',
        'media_type': 'image'
    },
]

def seed_database():
    print("🌱 Seeding database with sample posts...\n")
    
    success_count = 0
    for post_data in sample_posts:
        try:
            Post.create_post(
                post_id=post_data['post_id'],
                name=post_data['name'],
                caption=post_data['caption'],
                media_url=post_data['media_url'],
                media_type=post_data['media_type']
            )
            print(f"✓ Created: {post_data['post_id']} - {post_data['name']}")
            success_count += 1
        except Exception as e:
            print(f"✗ Error creating {post_data['post_id']}: {e}")
    
    print(f"\n✅ Successfully seeded {success_count}/{len(sample_posts)} posts!")

if __name__ == '__main__':
    seed_database()