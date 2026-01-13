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
    {
        'post_id': 'post_016',
        'name': 'Tech Reviewer Mike',
        'caption': 'Unboxing the latest MacBook Pro M3! This laptop is insanely fast. Perfect for video editing and coding. #apple #macbook #tech',
        'media_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8',
        'media_type': 'image'
    },
    {
        'post_id': 'post_017',
        'name': 'Gadget Girl',
        'caption': 'New wireless earbuds review! Noise cancellation is top-notch. Battery life lasts all day. #audio #wireless #tech',
        'media_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df',
        'media_type': 'image'
    },
    {
        'post_id': 'post_018',
        'name': 'Gaming Pro',
        'caption': 'Building my dream gaming PC! RTX 4090 graphics card installed. Ready for 4K gaming at 144fps. #pc #gaming #nvidia',
        'media_url': 'https://images.unsplash.com/photo-1587202372634-32705e3bf49c',
        'media_type': 'image'
    },
    {
        'post_id': 'post_019',
        'name': 'Smart Home Hub',
        'caption': 'Smart home automation complete! Voice control for lights, thermostat, and security. Living in the future! #smarthome #iot #automation',
        'media_url': 'https://images.unsplash.com/photo-1558002038-1055907df827',
        'media_type': 'image'
    },
    {
        'post_id': 'post_020',
        'name': 'VR Explorer',
        'caption': 'Virtual reality gaming is mind-blowing! Just played the latest VR horror game. So immersive! #vr #virtualreality #gaming',
        'media_url': 'https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac',
        'media_type': 'image'
    },
    {
        'post_id': 'post_021',
        'name': 'Drone Pilot Dave',
        'caption': 'Captured stunning aerial footage with my new drone! 4K video quality is incredible. #drone #aerial #photography',
        'media_url': 'https://images.unsplash.com/photo-1473968512647-3e447244af8f',
        'media_type': 'image'
    },
    {
        'post_id': 'post_022',
        'name': 'Tablet Reviewer',
        'caption': 'iPad Pro vs Surface Pro comparison! Drawing on tablets has never been better. #tablet #digital #art',
        'media_url': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0',
        'media_type': 'image'
    },
    {
        'post_id': 'post_023',
        'name': 'Camera Enthusiast',
        'caption': 'New mirrorless camera unboxing! Full frame sensor with incredible low-light performance. #camera #photography #mirrorless',
        'media_url': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd',
        'media_type': 'image'
    },
    {
        'post_id': 'post_024',
        'name': 'Wearable Tech',
        'caption': 'Smartwatch fitness tracking for the win! Monitoring heart rate, sleep, and activity. Health data at my wrist. #smartwatch #fitness #health',
        'media_url': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a',
        'media_type': 'image'
    },
    {
        'post_id': 'post_025',
        'name': 'Mechanical Keys',
        'caption': 'Custom mechanical keyboard build complete! Clicky switches and RGB lighting. Typing feels amazing! #keyboard #mechanical #gaming',
        'media_url': 'https://images.unsplash.com/photo-1595225476474-87563907a212',
        'media_type': 'image'
    },
    
    # Food & Cooking (10 posts)
    {
        'post_id': 'post_026',
        'name': 'Chef Julia',
        'caption': 'Homemade pasta from scratch! Fresh ingredients make all the difference. Recipe coming soon. #pasta #italian #cooking',
        'media_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9',
        'media_type': 'image'
    },
    {
        'post_id': 'post_027',
        'name': 'Sushi Master',
        'caption': 'Sushi rolling tutorial! Perfect rice, fresh fish, and precision cuts. Japanese cuisine at its finest. #sushi #japanese #food',
        'media_url': 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351',
        'media_type': 'image'
    },
    {
        'post_id': 'post_028',
        'name': 'BBQ Boss',
        'caption': 'Slow-smoked brisket for 14 hours! Tender, juicy, and full of flavor. BBQ perfection achieved. #bbq #smoking #meat',
        'media_url': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1',
        'media_type': 'image'
    },
    {
        'post_id': 'post_029',
        'name': 'Dessert Queen',
        'caption': 'Triple chocolate cake with ganache! Decadent layers of pure chocolate heaven. #cake #dessert #chocolate',
        'media_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587',
        'media_type': 'image'
    },
    {
        'post_id': 'post_030',
        'name': 'Healthy Eats',
        'caption': 'Buddha bowl with quinoa, avocado, and roasted veggies! Nutritious and delicious meal prep. #healthy #vegan #mealprep',
        'media_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c',
        'media_type': 'image'
    },
    {
        'post_id': 'post_031',
        'name': 'Bread Baker',
        'caption': 'Sourdough bread baking success! Crispy crust and airy interior. Nothing beats homemade bread. #sourdough #baking #bread',
        'media_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff',
        'media_type': 'image'
    },
    {
        'post_id': 'post_032',
        'name': 'Coffee Addict',
        'caption': 'Latte art perfection! Practicing my pour technique. Coffee tastes better when it looks good. #coffee #latte #barista',
        'media_url': 'https://images.unsplash.com/photo-1511920170033-f8396924c348',
        'media_type': 'image'
    },
    {
        'post_id': 'post_033',
        'name': 'Taco Tuesday',
        'caption': 'Street tacos with homemade salsa! Authentic Mexican flavors. Taco night is the best night. #tacos #mexican #food',
        'media_url': 'https://images.unsplash.com/photo-1565299507177-b0ac66763828',
        'media_type': 'image'
    },
    {
        'post_id': 'post_034',
        'name': 'Smoothie Pro',
        'caption': 'Green smoothie packed with spinach, banana, and protein! Healthy breakfast on the go. #smoothie #healthy #breakfast',
        'media_url': 'https://images.unsplash.com/photo-1505252585461-04db1eb84625',
        'media_type': 'image'
    },
    {
        'post_id': 'post_035',
        'name': 'Burger Master',
        'caption': 'Ultimate cheeseburger with bacon and special sauce! Juicy patty and fresh toppings. Burger goals! #burger #food #yum',
        'media_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd',
        'media_type': 'image'
    },
    
    # Travel & Adventure (10 posts)
    {
        'post_id': 'post_036',
        'name': 'Wanderlust Sarah',
        'caption': 'Exploring the streets of Paris! Eiffel Tower views and croissants. Dream vacation come true. #paris #france #travel',
        'media_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34',
        'media_type': 'image'
    },
    {
        'post_id': 'post_037',
        'name': 'Mountain Climber',
        'caption': 'Summit reached! Climbed to the top of Mount Kilimanjaro. Breathtaking views above the clouds. #climbing #mountain #adventure',
        'media_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4',
        'media_type': 'image'
    },
    {
        'post_id': 'post_038',
        'name': 'Beach Bum',
        'caption': 'Tropical paradise in Maldives! Crystal clear water and white sand beaches. Living the island life. #maldives #beach #paradise',
        'media_url': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8',
        'media_type': 'image'
    },
    {
        'post_id': 'post_039',
        'name': 'Safari Guide',
        'caption': 'African safari adventure! Spotted lions, elephants, and giraffes in their natural habitat. Wildlife photography at its best. #safari #africa #wildlife',
        'media_url': 'https://images.unsplash.com/photo-1516426122078-c23e76319801',
        'media_type': 'image'
    },
    {
        'post_id': 'post_040',
        'name': 'City Explorer',
        'caption': 'Tokyo nightlife is electric! Neon lights, bustling streets, and amazing food. Urban exploration goals. #tokyo #japan #city',
        'media_url': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf',
        'media_type': 'image'
    },
    {
        'post_id': 'post_041',
        'name': 'Road Tripper',
        'caption': 'Cross-country road trip through Route 66! Classic American adventure with amazing scenery. #roadtrip #travel #usa',
        'media_url': 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800',
        'media_type': 'image'
    },
    {
        'post_id': 'post_042',
        'name': 'Scuba Diver',
        'caption': 'Underwater world of the Great Barrier Reef! Colorful coral and tropical fish everywhere. Marine life is amazing. #scuba #diving #ocean',
        'media_url': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5',
        'media_type': 'image'
    },
    {
        'post_id': 'post_043',
        'name': 'Desert Wanderer',
        'caption': 'Camping under the stars in the Sahara Desert! Sand dunes and endless sky. Peaceful solitude. #desert #camping #sahara',
        'media_url': 'https://images.unsplash.com/photo-1509316785289-025f5b846b35',
        'media_type': 'image'
    },
    {
        'post_id': 'post_044',
        'name': 'Aurora Chaser',
        'caption': 'Northern lights in Iceland! Dancing green lights across the night sky. Bucket list moment achieved. #aurora #iceland #northernlights',
        'media_url': 'https://images.unsplash.com/photo-1483347756197-71ef80e95f73',
        'media_type': 'image'
    },
    {
        'post_id': 'post_045',
        'name': 'Temple Tourist',
        'caption': 'Ancient temples of Angkor Wat at sunrise! Historical architecture and spiritual atmosphere. Cambodia is incredible. #angkorwat #cambodia #temple',
        'media_url': 'https://images.unsplash.com/photo-1563492065599-3520f775eeed',
        'media_type': 'image'
    },
    
    # Fitness & Sports (10 posts)
    {
        'post_id': 'post_046',
        'name': 'CrossFit Coach',
        'caption': 'Morning WOD completed! Heavy deadlifts and box jumps. Building strength every day. #crossfit #workout #fitness',
        'media_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b',
        'media_type': 'image'
    },
    {
        'post_id': 'post_047',
        'name': 'Marathon Runner',
        'caption': 'Just finished my first marathon! 26.2 miles of pure determination. Feeling accomplished and exhausted. #marathon #running #fitness',
        'media_url': 'https://images.unsplash.com/photo-1552674605-db6ffd4facb5',
        'media_type': 'image'
    },
    {
        'post_id': 'post_048',
        'name': 'Swimmer Sarah',
        'caption': 'Pool training session! Working on my freestyle technique. Swimming is the best full-body workout. #swimming #pool #training',
        'media_url': 'https://images.unsplash.com/photo-1519315901367-f34ff9154487',
        'media_type': 'image'
    },
    {
        'post_id': 'post_049',
        'name': 'Cyclist Mike',
        'caption': '100km bike ride through countryside! Fresh air and beautiful landscapes. Cycling is my meditation. #cycling #bike #outdoors',
        'media_url': 'https://images.unsplash.com/photo-1541625602330-2277a4c46182',
        'media_type': 'image'
    },
    {
        'post_id': 'post_050',
        'name': 'Boxing Champion',
        'caption': 'Heavy bag training! Working on combinations and footwork. Boxing is the ultimate cardio workout. #boxing #training #fitness',
        'media_url': 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed',
        'media_type': 'image'
    },
    {
        'post_id': 'post_051',
        'name': 'Rock Climber',
        'caption': 'Indoor climbing session! Conquered the hardest route in the gym. Upper body strength on point. #climbing #bouldering #fitness',
        'media_url': 'https://images.unsplash.com/photo-1522163182402-834f871fd851',
        'media_type': 'image'
    },
    {
        'post_id': 'post_052',
        'name': 'Pilates Pro',
        'caption': 'Pilates reformer class! Core strength and flexibility training. Mind-body connection achieved. #pilates #fitness #wellness',
        'media_url': 'https://images.unsplash.com/photo-1518611012118-696072aa579a',
        'media_type': 'image'
    },
    {
        'post_id': 'post_053',
        'name': 'Basketball Player',
        'caption': 'Pickup basketball game at the park! Nothing beats the competition and teamwork. Ball is life! #basketball #sports #hoops',
        'media_url': 'https://images.unsplash.com/photo-1546519638-68e109498ffc',
        'media_type': 'image'
    },
    {
        'post_id': 'post_054',
        'name': 'Tennis Coach',
        'caption': 'Tennis practice on a beautiful day! Working on my serve and backhand. Love this sport. #tennis #sports #training',
        'media_url': 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8',
        'media_type': 'image'
    },
    {
        'post_id': 'post_055',
        'name': 'Hiker Hannah',
        'caption': 'Trail running in the mountains! Fresh air, beautiful views, and natural terrain. Best cardio ever. #hiking #running #nature',
        'media_url': 'https://images.unsplash.com/photo-1551632811-561732d1e306',
        'media_type': 'image'
    },
    
    # Art & Creativity (10 posts)
    {
        'post_id': 'post_056',
        'name': 'Digital Artist',
        'caption': 'New digital painting complete! Vibrant colors and fantasy landscapes. Digital art is limitless. #digitalart #painting #artist',
        'media_url': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f',
        'media_type': 'image'
    },
    {
        'post_id': 'post_057',
        'name': 'Graffiti King',
        'caption': 'Street art mural finished! Bold colors and powerful message. Urban art at its finest. #graffiti #streetart #mural',
        'media_url': 'https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8',
        'media_type': 'image'
    },
    {
        'post_id': 'post_058',
        'name': 'Watercolor Artist',
        'caption': 'Watercolor landscape painting! Soft colors blending beautifully. Traditional art techniques never go out of style. #watercolor #painting #art',
        'media_url': 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b',
        'media_type': 'image'
    },
    {
        'post_id': 'post_059',
        'name': 'Sculptor Sam',
        'caption': 'Clay sculpture in progress! Working with my hands to create 3D art. Sculpting is meditation. #sculpture #clay #art',
        'media_url': 'https://images.unsplash.com/photo-1452860606245-08befc0ff44b',
        'media_type': 'image'
    },
    {
        'post_id': 'post_060',
        'name': 'Calligraphy Master',
        'caption': 'Modern calligraphy practice! Beautiful lettering with brush pens. The art of writing. #calligraphy #lettering #art',
        'media_url': 'https://images.unsplash.com/photo-1455390582262-044cdead277a',
        'media_type': 'image'
    },
    {
        'post_id': 'post_061',
        'name': 'Portrait Painter',
        'caption': 'Oil portrait painting session! Capturing human emotion on canvas. Realistic art takes patience. #portrait #oilpainting #art',
        'media_url': 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b',
        'media_type': 'image'
    },
    {
        'post_id': 'post_062',
        'name': 'Abstract Artist',
        'caption': 'Abstract expressionism piece! Bold brushstrokes and emotional colors. Art without boundaries. #abstract #modernart #painting',
        'media_url': 'https://images.unsplash.com/photo-1541961017774-22349e4a1262',
        'media_type': 'image'
    },
    {
        'post_id': 'post_063',
        'name': 'Tattoo Artist',
        'caption': 'Custom tattoo design complete! Intricate line work and shading. Permanent art on skin. #tattoo #art #bodyart',
        'media_url': 'https://images.unsplash.com/photo-1611501275019-9b5cda994e8d',
        'media_type': 'image'
    },
    {
        'post_id': 'post_064',
        'name': 'Ceramics Creator',
        'caption': 'Handmade pottery on the wheel! Creating functional art pieces. Clay therapy at its best. #pottery #ceramics #handmade',
        'media_url': 'https://images.unsplash.com/photo-1493106641515-6b5631de4bb9',
        'media_type': 'image'
    },
    {
        'post_id': 'post_065',
        'name': 'Graphic Designer',
        'caption': 'New logo design for a startup! Clean lines and modern aesthetics. Branding matters. #graphicdesign #logo #branding',
        'media_url': 'https://images.unsplash.com/photo-1626785774573-4b799315345d',
        'media_type': 'image'
    },
    
]

def seed_database():
    print("seeding database with sample posts...\n")
    
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
            print(f"Created: {post_data['post_id']} - {post_data['name']}")
            success_count += 1
        except Exception as e:
            print(f"error creating {post_data['post_id']}: {e}")
    
    print(f"\n Successfully seeded {success_count}/{len(sample_posts)} posts!")

if __name__ == '__main__':
    seed_database()
