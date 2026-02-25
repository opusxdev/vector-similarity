import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

QDRANT_URL           = os.getenv('QDRANT_URL')
QDRANT_API_KEY       = os.getenv('QDRANT_API_KEY')
MONGODB_URI          = os.getenv('MONGODB_URI') or os.getenv('MONGO_URI') or os.getenv('DATABASE_URL')
EMBEDDING_SERVICE_URL = os.getenv('EMBEDDING_SERVICE_URL', 'http://localhost:8001')
COLLECTION_NAME      = 'social_posts'


missing = [k for k, v in {'QDRANT_URL': QDRANT_URL, 'QDRANT_API_KEY': QDRANT_API_KEY}.items() if not v]
if missing:
    print(f"missing env vars: {', '.join(missing)}")
    sys.exit(1)

print(f"qdrant: {QDRANT_URL}")
print(f"embedding service: {EMBEDDING_SERVICE_URL}")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
except ImportError:
    print("Installing qdrant-client...")
    os.system(f"{sys.executable} -m pip install qdrant-client --quiet")
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def ensure_collection(dim=384):
    try:
        qdrant.get_collection(COLLECTION_NAME)
        print(f"✓ Collection '{COLLECTION_NAME}' exists")
    except Exception:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )
        print(f"✓ Created collection '{COLLECTION_NAME}'")

def get_embedding(text):
    r = requests.post(f"{EMBEDDING_SERVICE_URL}/embed", json={"text": text}, timeout=15)
    r.raise_for_status()
    return r.data['embedding'] if hasattr(r, 'data') else r.json()['embedding']

# seedPosts 
sample_posts = [
    {'post_id':'post_001','name':'John Doe','caption':'Beautiful sunset at the beach! Perfect evening with family. #sunset #beach #nature','media_url':'https://images.unsplash.com/photo-1507525428034-b723cf961d3e','media_type':'image','category':'nature'},
    {'post_id':'post_002','name':'Sarah Smith','caption':'New smartphone unboxing! This camera quality is amazing. Best tech purchase of 2024. #tech #smartphone','media_url':'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9','media_type':'image','category':'tech'},
    {'post_id':'post_003','name':'Mike Johnson','caption':'Workout complete! Leg day is the hardest but most rewarding. #fitness #gym #motivation','media_url':'https://images.unsplash.com/photo-1534438327276-14e5300c3a48','media_type':'image','category':'healthcare'},
    {'post_id':'post_004','name':'Emma Wilson','caption':'Homemade pizza night! Fresh ingredients make all the difference. Recipe coming soon. #food #cooking','media_url':'https://images.unsplash.com/photo-1513104890138-7c749659a591','media_type':'image','category':'food'},
    {'post_id':'post_005','name':'David Lee','caption':'Morning coffee and coding session. Building something exciting! #developer #tech #coffee #coding','media_url':'https://images.unsplash.com/photo-1498050108023-c5249f4df085','media_type':'image','category':'tech'},
    {'post_id':'post_006','name':'Lisa Brown','caption':'Makeup tutorial coming soon! This look is gorgeous. #beauty #makeup #tutorial','media_url':'https://images.unsplash.com/photo-1512496015851-a90fb38ba796','media_type':'image','category':'art'},
    {'post_id':'post_007','name':'Tom Harris','caption':'Mountain hiking adventure! The view from the top was breathtaking. #hiking #nature #adventure #mountains','media_url':'https://images.unsplash.com/photo-1551632811-561732d1e306','media_type':'image','category':'nature'},
    {'post_id':'post_008','name':'Anna Martinez','caption':'New book recommendations! Just finished this amazing thriller novel. Page turner! #reading #books #thriller','media_url':'https://images.unsplash.com/photo-1512820790803-83ca734da794','media_type':'image','category':'education'},
    {'post_id':'post_009','name':'Chris Taylor','caption':'Gaming setup complete! Ready for the weekend gaming marathon. RGB everything! #gaming #setup #tech #rgb','media_url':'https://images.unsplash.com/photo-1593305841991-05c297ba4575','media_type':'image','category':'tech'},
    {'post_id':'post_010','name':'Jennifer White','caption':'Travel diaries: Exploring ancient architecture in Rome. History comes alive here! #travel #rome #architecture','media_url':'https://images.unsplash.com/photo-1552832230-c0197dd311b5','media_type':'image','category':'travel'},
    {'post_id':'post_011','name':'Robert Green','caption':'Yoga session at sunrise. Finding inner peace. #yoga #wellness #meditation #morning','media_url':'https://images.unsplash.com/photo-1506126613408-eca07ce68773','media_type':'image','category':'healthcare'},
    {'post_id':'post_012','name':'Maria Garcia','caption':'Fashion week ready! New collection. Style is a way to say who you are. #fashion #style #outfit','media_url':'https://images.unsplash.com/photo-1483985988355-763728e1935b','media_type':'image','category':'art'},
    {'post_id':'post_013','name':'Kevin Brown','caption':'Street photography in Tokyo. Urban life at its finest. #photography #tokyo #urban #street','media_url':'https://images.unsplash.com/photo-1536098561742-ca998e48cbcc','media_type':'image','category':'travel'},
    {'post_id':'post_014','name':'Sophie Davis','caption':'Baking therapy! Fresh croissants from scratch. The smell is heavenly! #baking #croissants #food','media_url':'https://images.unsplash.com/photo-1555507036-ab1f4038808a','media_type':'image','category':'food'},
    {'post_id':'post_015','name':'Alex Turner','caption':'Music production session. Creating beats late at night. #music #producer #beats #studio','media_url':'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04','media_type':'image','category':'music'},
    {'post_id':'post_016','name':'Tech Reviewer Mike','caption':'Unboxing the latest MacBook Pro M3! This laptop is insanely fast. Perfect for video editing and coding. #apple #macbook #tech','media_url':'https://images.unsplash.com/photo-1517336714731-489689fd1ca8','media_type':'image','category':'tech'},
    {'post_id':'post_017','name':'Gadget Girl','caption':'New wireless earbuds review! Noise cancellation is top-notch. Battery life lasts all day. #audio #wireless #tech','media_url':'https://images.unsplash.com/photo-1590658268037-6bf12165a8df','media_type':'image','category':'tech'},
    {'post_id':'post_018','name':'Gaming Pro','caption':'Building my dream gaming PC! RTX 4090 graphics card installed. Ready for 4K gaming at 144fps. #pc #gaming #nvidia','media_url':'https://images.unsplash.com/photo-1587202372634-32705e3bf49c','media_type':'image','category':'tech'},
    {'post_id':'post_019','name':'Smart Home Hub','caption':'Smart home automation complete! Voice control for lights, thermostat, and security. Living in the future! #smarthome #iot #automation','media_url':'https://images.unsplash.com/photo-1558002038-1055907df827','media_type':'image','category':'tech'},
    {'post_id':'post_020','name':'VR Explorer','caption':'Virtual reality gaming is mind-blowing! Just played the latest VR horror game. So immersive! #vr #virtualreality #gaming','media_url':'https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac','media_type':'image','category':'tech'},
    {'post_id':'post_021','name':'Drone Pilot Dave','caption':'Captured stunning aerial footage with my new drone! 4K video quality is incredible. #drone #aerial #photography','media_url':'https://images.unsplash.com/photo-1473968512647-3e447244af8f','media_type':'image','category':'tech'},
    {'post_id':'post_022','name':'Tablet Reviewer','caption':'iPad Pro vs Surface Pro comparison! Drawing on tablets has never been better. #tablet #digital #art','media_url':'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0','media_type':'image','category':'tech'},
    {'post_id':'post_023','name':'Camera Enthusiast','caption':'New mirrorless camera unboxing! Full frame sensor with incredible low-light performance. #camera #photography #mirrorless','media_url':'https://images.unsplash.com/photo-1502920917128-1aa500764cbd','media_type':'image','category':'tech'},
    {'post_id':'post_024','name':'Wearable Tech','caption':'Smartwatch fitness tracking for the win! Monitoring heart rate, sleep, and activity. Health data at my wrist. #smartwatch #fitness #health','media_url':'https://images.unsplash.com/photo-1579586337278-3befd40fd17a','media_type':'image','category':'tech'},
    {'post_id':'post_025','name':'Mechanical Keys','caption':'Custom mechanical keyboard build complete! Clicky switches and RGB lighting. Typing feels amazing! #keyboard #mechanical #gaming','media_url':'https://images.unsplash.com/photo-1595225476474-87563907a212','media_type':'image','category':'tech'},
    {'post_id':'post_026','name':'Chef Julia','caption':'Homemade pasta from scratch! Fresh ingredients make all the difference. Recipe coming soon. #pasta #italian #cooking','media_url':'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9','media_type':'image','category':'food'},
    {'post_id':'post_027','name':'Sushi Master','caption':'Sushi rolling tutorial! Perfect rice, fresh fish, and precision cuts. Japanese cuisine at its finest. #sushi #japanese #food','media_url':'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351','media_type':'image','category':'food'},
    {'post_id':'post_028','name':'BBQ Boss','caption':'Slow-smoked brisket for 14 hours! Tender, juicy, and full of flavor. BBQ perfection achieved. #bbq #smoking #meat','media_url':'https://images.unsplash.com/photo-1555939594-58d7cb561ad1','media_type':'image','category':'food'},
    {'post_id':'post_029','name':'Dessert Queen','caption':'Triple chocolate cake with ganache! Decadent layers of pure chocolate heaven. #cake #dessert #chocolate','media_url':'https://images.unsplash.com/photo-1578985545062-69928b1d9587','media_type':'image','category':'food'},
    {'post_id':'post_030','name':'Healthy Eats','caption':'Buddha bowl with quinoa, avocado, and roasted veggies! Nutritious and delicious meal prep. #healthy #vegan #mealprep','media_url':'https://images.unsplash.com/photo-1546069901-ba9599a7e63c','media_type':'image','category':'food'},
    {'post_id':'post_031','name':'Bread Baker','caption':'Sourdough bread baking success! Crispy crust and airy interior. Nothing beats homemade bread. #sourdough #baking #bread','media_url':'https://images.unsplash.com/photo-1509440159596-0249088772ff','media_type':'image','category':'food'},
    {'post_id':'post_032','name':'Coffee Addict','caption':'Latte art perfection! Practicing my pour technique. Coffee tastes better when it looks good. #coffee #latte #barista','media_url':'https://images.unsplash.com/photo-1511920170033-f8396924c348','media_type':'image','category':'food'},
    {'post_id':'post_033','name':'Taco Tuesday','caption':'Street tacos with homemade salsa! Authentic Mexican flavors. Taco night is the best night. #tacos #mexican #food','media_url':'https://images.unsplash.com/photo-1565299507177-b0ac66763828','media_type':'image','category':'food'},
    {'post_id':'post_034','name':'Smoothie Pro','caption':'Green smoothie packed with spinach, banana, and protein! Healthy breakfast on the go. #smoothie #healthy #breakfast','media_url':'https://images.unsplash.com/photo-1505252585461-04db1eb84625','media_type':'image','category':'food'},
    {'post_id':'post_035','name':'Burger Master','caption':'Ultimate cheeseburger with bacon and special sauce! Juicy patty and fresh toppings. Burger goals! #burger #food #yum','media_url':'https://images.unsplash.com/photo-1568901346375-23c9450c58cd','media_type':'image','category':'food'},
    {'post_id':'post_036','name':'Wanderlust Sarah','caption':'Exploring the streets of Paris! Eiffel Tower views and croissants. Dream vacation come true. #paris #france #travel','media_url':'https://images.unsplash.com/photo-1502602898657-3e91760cbb34','media_type':'image','category':'travel'},
    {'post_id':'post_037','name':'Mountain Climber','caption':'Summit reached! Climbed to the top of Mount Kilimanjaro. Breathtaking views above the clouds. #climbing #mountain #adventure','media_url':'https://images.unsplash.com/photo-1506905925346-21bda4d32df4','media_type':'image','category':'travel'},
    {'post_id':'post_038','name':'Beach Bum','caption':'Tropical paradise in Maldives! Crystal clear water and white sand beaches. Living the island life. #maldives #beach #paradise','media_url':'https://images.unsplash.com/photo-1514282401047-d79a71a590e8','media_type':'image','category':'travel'},
    {'post_id':'post_039','name':'Safari Guide','caption':'African safari adventure! Spotted lions, elephants, and giraffes in their natural habitat. Wildlife photography at its best. #safari #africa #wildlife','media_url':'https://images.unsplash.com/photo-1516426122078-c23e76319801','media_type':'image','category':'travel'},
    {'post_id':'post_040','name':'City Explorer','caption':'Tokyo nightlife is electric! Neon lights, bustling streets, and amazing food. Urban exploration goals. #tokyo #japan #city','media_url':'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf','media_type':'image','category':'travel'},
    {'post_id':'post_041','name':'Road Tripper','caption':'Cross-country road trip through Route 66! Classic American adventure with amazing scenery. #roadtrip #travel #usa','media_url':'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800','media_type':'image','category':'travel'},
    {'post_id':'post_042','name':'Scuba Diver','caption':'Underwater world of the Great Barrier Reef! Colorful coral and tropical fish everywhere. Marine life is amazing. #scuba #diving #ocean','media_url':'https://images.unsplash.com/photo-1544551763-46a013bb70d5','media_type':'image','category':'travel'},
    {'post_id':'post_043','name':'Desert Wanderer','caption':'Camping under the stars in the Sahara Desert! Sand dunes and endless sky. Peaceful solitude. #desert #camping #sahara','media_url':'https://images.unsplash.com/photo-1509316785289-025f5b846b35','media_type':'image','category':'travel'},
    {'post_id':'post_044','name':'Aurora Chaser','caption':'Northern lights in Iceland! Dancing green lights across the night sky. Bucket list moment achieved. #aurora #iceland #northernlights','media_url':'https://images.unsplash.com/photo-1483347756197-71ef80e95f73','media_type':'image','category':'travel'},
    {'post_id':'post_045','name':'Temple Tourist','caption':'Ancient temples of Angkor Wat at sunrise! Historical architecture and spiritual atmosphere. Cambodia is incredible. #angkorwat #cambodia #temple','media_url':'https://images.unsplash.com/photo-1563492065599-3520f775eeed','media_type':'image','category':'travel'},
    {'post_id':'post_046','name':'CrossFit Coach','caption':'Morning WOD completed! Heavy deadlifts and box jumps. Building strength every day. #crossfit #workout #fitness','media_url':'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b','media_type':'image','category':'sports'},
    {'post_id':'post_047','name':'Marathon Runner','caption':'Just finished my first marathon! 26.2 miles of pure determination. Feeling accomplished and exhausted. #marathon #running #fitness','media_url':'https://images.unsplash.com/photo-1552674605-db6ffd4facb5','media_type':'image','category':'sports'},
    {'post_id':'post_048','name':'Swimmer Sarah','caption':'Pool training session! Working on my freestyle technique. Swimming is the best full-body workout. #swimming #pool #training','media_url':'https://images.unsplash.com/photo-1519315901367-f34ff9154487','media_type':'image','category':'sports'},
    {'post_id':'post_049','name':'Cyclist Mike','caption':'100km bike ride through countryside! Fresh air and beautiful landscapes. Cycling is my meditation. #cycling #bike #outdoors','media_url':'https://images.unsplash.com/photo-1541625602330-2277a4c46182','media_type':'image','category':'sports'},
    {'post_id':'post_050','name':'Boxing Champion','caption':'Heavy bag training! Working on combinations and footwork. Boxing is the ultimate cardio workout. #boxing #training #fitness','media_url':'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed','media_type':'image','category':'sports'},
    {'post_id':'post_051','name':'Rock Climber','caption':'Indoor climbing session! Conquered the hardest route in the gym. Upper body strength on point. #climbing #bouldering #fitness','media_url':'https://images.unsplash.com/photo-1522163182402-834f871fd851','media_type':'image','category':'sports'},
    {'post_id':'post_052','name':'Pilates Pro','caption':'Pilates reformer class! Core strength and flexibility training. Mind-body connection achieved. #pilates #fitness #wellness','media_url':'https://images.unsplash.com/photo-1518611012118-696072aa579a','media_type':'image','category':'healthcare'},
    {'post_id':'post_053','name':'Basketball Player','caption':'Pickup basketball game at the park! Nothing beats the competition and teamwork. Ball is life! #basketball #sports #hoops','media_url':'https://images.unsplash.com/photo-1546519638-68e109498ffc','media_type':'image','category':'sports'},
    {'post_id':'post_054','name':'Tennis Coach','caption':'Tennis practice on a beautiful day! Working on my serve and backhand. Love this sport. #tennis #sports #training','media_url':'https://images.unsplash.com/photo-1554068865-24cecd4e34b8','media_type':'image','category':'sports'},
    {'post_id':'post_055','name':'Hiker Hannah','caption':'Trail running in the mountains! Fresh air, beautiful views, and natural terrain. Best cardio ever. #hiking #running #nature','media_url':'https://images.unsplash.com/photo-1551632811-561732d1e306','media_type':'image','category':'sports'},
    {'post_id':'post_056','name':'Digital Artist','caption':'New digital painting complete! Vibrant colors and fantasy landscapes. Digital art is limitless. #digitalart #painting #artist','media_url':'https://images.unsplash.com/photo-1513364776144-60967b0f800f','media_type':'image','category':'art'},
    {'post_id':'post_057','name':'Graffiti King','caption':'Street art mural finished! Bold colors and powerful message. Urban art at its finest. #graffiti #streetart #mural','media_url':'https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8','media_type':'image','category':'art'},
    {'post_id':'post_058','name':'Watercolor Artist','caption':'Watercolor landscape painting! Soft colors blending beautifully. Traditional art techniques never go out of style. #watercolor #painting #art','media_url':'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b','media_type':'image','category':'art'},
    {'post_id':'post_059','name':'Sculptor Sam','caption':'Clay sculpture in progress! Working with my hands to create 3D art. Sculpting is meditation. #sculpture #clay #art','media_url':'https://images.unsplash.com/photo-1452860606245-08befc0ff44b','media_type':'image','category':'art'},
    {'post_id':'post_060','name':'Calligraphy Master','caption':'Modern calligraphy practice! Beautiful lettering with brush pens. The art of writing. #calligraphy #lettering #art','media_url':'https://images.unsplash.com/photo-1455390582262-044cdead277a','media_type':'image','category':'art'},
    {'post_id':'post_061','name':'Portrait Painter','caption':'Oil portrait painting session! Capturing human emotion on canvas. Realistic art takes patience. #portrait #oilpainting #art','media_url':'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b','media_type':'image','category':'art'},
    {'post_id':'post_062','name':'Abstract Artist','caption':'Abstract expressionism piece! Bold brushstrokes and emotional colors. Art without boundaries. #abstract #modernart #painting','media_url':'https://images.unsplash.com/photo-1541961017774-22349e4a1262','media_type':'image','category':'art'},
    {'post_id':'post_063','name':'Tattoo Artist','caption':'Custom tattoo design complete! Intricate line work and shading. Permanent art on skin. #tattoo #art #bodyart','media_url':'https://images.unsplash.com/photo-1611501275019-9b5cda994e8d','media_type':'image','category':'art'},
    {'post_id':'post_064','name':'Ceramics Creator','caption':'Handmade pottery on the wheel! Creating functional art pieces. Clay therapy at its best. #pottery #ceramics #handmade','media_url':'https://images.unsplash.com/photo-1493106641515-6b5631de4bb9','media_type':'image','category':'art'},
    {'post_id':'post_065','name':'Graphic Designer','caption':'New logo design for a startup! Clean lines and modern aesthetics. Branding matters. #graphicdesign #logo #branding','media_url':'https://images.unsplash.com/photo-1626785774573-4b799315345d','media_type':'image','category':'art'},
    {'post_id':'post_066','name':'Tech Reviewer','caption':'Hands-on with the latest smartphone. Sleek design and powerful performance. #tech #gadgets','media_url':'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9','media_type':'image','category':'tech'},
    {'post_id':'post_067','name':'Gadget Hub','caption':'Wireless earbuds with immersive sound and long battery life. #audio #tech','media_url':'https://images.unsplash.com/photo-1590658268037-6bf12165a8df','media_type':'image','category':'tech'},
    {'post_id':'post_068','name':'Wearable World','caption':'Smartwatch tracking health, fitness, and notifications. #wearables','media_url':'https://images.unsplash.com/photo-1523275335684-37898b6baf30','media_type':'image','category':'tech'},
    {'post_id':'post_069','name':'Laptop Studio','caption':'Ultra-slim laptop built for productivity and creativity. #laptop','media_url':'https://images.unsplash.com/photo-1517336714731-489689fd1ca8','media_type':'image','category':'tech'},
    {'post_id':'post_070','name':'Gaming Zone','caption':'Next-gen gaming console delivering stunning visuals. #gaming','media_url':'https://images.unsplash.com/photo-1606813909355-89d3d2b4e63f','media_type':'image','category':'tech'},
    {'post_id':'post_071','name':'Camera Lab','caption':'Mirrorless camera for professional photography. #camera','media_url':'https://images.unsplash.com/photo-1519183071298-a2962eadcdb2','media_type':'image','category':'tech'},
    {'post_id':'post_072','name':'Desk Setup','caption':'Minimal desk setup with powerful tech gear. #workspace','media_url':'https://images.unsplash.com/photo-1527430253228-e93688616381','media_type':'image','category':'tech'},
    {'post_id':'post_073','name':'Smart Living','caption':'Smart home devices making life easier. #smarthome','media_url':'https://images.unsplash.com/photo-1558002038-1055907df827','media_type':'image','category':'tech'},
    {'post_id':'post_074','name':'Tablet Talk','caption':'Tablets designed for work and play. #tablet','media_url':'https://images.unsplash.com/photo-1585790050230-5dd28404ccb9','media_type':'image','category':'tech'},
    {'post_id':'post_075','name':'Tech Accessories','caption':'Accessories that complete your setup. #techaccessories','media_url':'https://images.unsplash.com/photo-1585386959984-a41552231693','media_type':'image','category':'tech'},
    {'post_id':'post_076','name':'AI Research','caption':'Artificial intelligence reshaping the future. #AI','media_url':'https://images.unsplash.com/photo-1581090700227-1e37b190418e','media_type':'image','category':'ai'},
    {'post_id':'post_077','name':'Neural Net','caption':'Neural networks powering smart systems. #MachineLearning','media_url':'https://images.unsplash.com/photo-1534751516642-a1af1ef26a56','media_type':'image','category':'ai'},
    {'post_id':'post_078','name':'Data Minds','caption':'Data-driven intelligence at scale. #DataScience','media_url':'https://images.unsplash.com/photo-1551288049-bebda4e38f71','media_type':'image','category':'ai'},
    {'post_id':'post_079','name':'AI Automation','caption':'Automation powered by artificial intelligence. #Automation','media_url':'https://images.unsplash.com/photo-1485827404703-89b55fcc595e','media_type':'image','category':'ai'},
    {'post_id':'post_080','name':'Vision AI','caption':'Computer vision enabling machines to see. #ComputerVision','media_url':'https://images.unsplash.com/photo-1581090464777-f3220bbe1b8b','media_type':'image','category':'ai'},
    {'post_id':'post_081','name':'AI Bots','caption':'Conversational AI changing user experiences. #Chatbots','media_url':'https://images.unsplash.com/photo-1531746790731-6c087fecd65a','media_type':'image','category':'ai'},
    {'post_id':'post_082','name':'ML Studio','caption':'Training models with real-world data. #ML','media_url':'https://images.unsplash.com/photo-1504639725590-34d0984388bd','media_type':'image','category':'ai'},
    {'post_id':'post_083','name':'AI Ethics','caption':'Building responsible and ethical AI. #AIEthics','media_url':'https://images.unsplash.com/photo-1603791440384-56cd371ee9a7','media_type':'image','category':'ai'},
    {'post_id':'post_084','name':'Robotics Lab','caption':'Robots powered by intelligent systems. #Robotics','media_url':'https://images.unsplash.com/photo-1485827404703-89b55fcc595e','media_type':'image','category':'ai'},
    {'post_id':'post_085','name':'AI Future','caption':'Exploring what is next for AI innovation. #FutureTech','media_url':'https://images.unsplash.com/photo-1518770660439-4636190af475','media_type':'image','category':'ai'},
    {'post_id':'post_086','name':'Healthcare Today','caption':'Modern hospitals improving patient outcomes. #healthcare','media_url':'https://images.unsplash.com/photo-1579684385127-1ef15d508118','media_type':'image','category':'healthcare'},
    {'post_id':'post_087','name':'Medical Staff','caption':'Doctors and nurses working on the frontlines. #medical','media_url':'https://images.unsplash.com/photo-1582750433449-648ed127bb54','media_type':'image','category':'healthcare'},
    {'post_id':'post_088','name':'Wellness Hub','caption':'Daily habits that support long-term wellness. #wellness','media_url':'https://images.unsplash.com/photo-1554284126-aa88f22d8b74','media_type':'image','category':'healthcare'},
    {'post_id':'post_089','name':'Medical Technology','caption':'Technology enhancing diagnosis and treatment. #medtech','media_url':'https://images.unsplash.com/photo-1581091012184-7d0e3b8f6f84','media_type':'image','category':'healthcare'},
    {'post_id':'post_090','name':'Patient Care','caption':'Patient-centered care makes all the difference. #patientcare','media_url':'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d','media_type':'image','category':'healthcare'},
    {'post_id':'post_091','name':'Mental Health Matters','caption':'Prioritizing mental health and self-care. #mentalhealth','media_url':'https://images.unsplash.com/photo-1527137342181-19aab11a8ee8','media_type':'image','category':'healthcare'},
    {'post_id':'post_092','name':'Fitness Care','caption':'Movement and exercise for better health. #fitness','media_url':'https://images.unsplash.com/photo-1558611848-73f7eb4001a1','media_type':'image','category':'healthcare'},
    {'post_id':'post_093','name':'Nutrition Guide','caption':'Balanced nutrition supports a healthy life. #nutrition','media_url':'https://images.unsplash.com/photo-1498837167922-ddd27525d352','media_type':'image','category':'healthcare'},
    {'post_id':'post_094','name':'Clinical Research','caption':'Research driving medical innovation forward. #clinicalresearch','media_url':'https://images.unsplash.com/photo-1582719478185-2f1f15c8a9a4','media_type':'image','category':'healthcare'},
    {'post_id':'post_095','name':'Healthcare Innovation','caption':'Innovations shaping the future of healthcare. #healthinnovation','media_url':'https://images.unsplash.com/photo-1538108149393-fbbd81895907','media_type':'image','category':'healthcare'},
    {'post_id':'post_096','name':'Crypto World','caption':'Decentralized finance is redefining money. #DeFi','media_url':'https://images.unsplash.com/photo-1621416894569-0f39ed31d247','media_type':'image','category':'web3'},
    {'post_id':'post_097','name':'Blockchain Hub','caption':'Blockchain technology enabling trustless systems. #blockchain','media_url':'https://images.unsplash.com/photo-1639322537228-f710d846310a','media_type':'image','category':'web3'},
    {'post_id':'post_098','name':'NFT Studio','caption':'NFTs changing digital ownership forever. #NFT','media_url':'https://images.unsplash.com/photo-1640161704729-cbe966a08476','media_type':'image','category':'web3'},
    {'post_id':'post_099','name':'DAO Network','caption':'Community-led governance through DAOs. #DAO','media_url':'https://images.unsplash.com/photo-1629726797843-6185f5f58f4c','media_type':'image','category':'web3'},
    {'post_id':'post_100','name':'Crypto Wallet','caption':'Secure storage for digital assets. #crypto','media_url':'https://images.unsplash.com/photo-1621768216002-5ac171876625','media_type':'image','category':'web3'},
    {'post_id':'post_101','name':'Metaverse Life','caption':'Exploring immersive virtual worlds. #metaverse','media_url':'https://images.unsplash.com/photo-1633356122544-f134324a6cee','media_type':'image','category':'web3'},
    {'post_id':'post_102','name':'Web3 Developer','caption':'Building decentralized applications. #dapps','media_url':'https://images.unsplash.com/photo-1518770660439-4636190af475','media_type':'image','category':'web3'},
    {'post_id':'post_103','name':'Crypto Mining','caption':'Mining operations powering blockchain networks. #mining','media_url':'https://images.unsplash.com/photo-1621416894569-0f39ed31d247','media_type':'image','category':'web3'},
    {'post_id':'post_104','name':'Token Economy','caption':'Token-based economies driving Web3 growth. #tokenomics','media_url':'https://images.unsplash.com/photo-1640340434855-6084b1f4901c','media_type':'image','category':'web3'},
    {'post_id':'post_105','name':'Web3 Future','caption':'The internet owned and governed by users. #web3','media_url':'https://images.unsplash.com/photo-1640340434855-6084b1f4901c','media_type':'image','category':'web3'},
    {'post_id':'post_106','name':'Content Creator','caption':'Creating content that connects audiences. #socialmedia','media_url':'https://images.unsplash.com/photo-1611162616475-46b635cb6868','media_type':'image','category':'socialmedia'},
    {'post_id':'post_107','name':'Influencer Life','caption':'Behind the scenes of influencer marketing. #influencer','media_url':'https://images.unsplash.com/photo-1557804506-669a67965ba0','media_type':'image','category':'socialmedia'},
    {'post_id':'post_108','name':'Social Growth','caption':'Scaling brands through social platforms. #marketing','media_url':'https://images.unsplash.com/photo-1542744173-8e7e53415bb0','media_type':'image','category':'socialmedia'},
    {'post_id':'post_109','name':'Viral Trends','caption':'Staying ahead of viral content trends. #trending','media_url':'https://images.unsplash.com/photo-1557426272-fc759fdf7a8d','media_type':'image','category':'socialmedia'},
    {'post_id':'post_110','name':'Creator Studio','caption':'Editing content for maximum engagement. #contentcreation','media_url':'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2','media_type':'image','category':'socialmedia'},
    {'post_id':'post_111','name':'Community Builder','caption':'Growing meaningful online communities. #community','media_url':'https://images.unsplash.com/photo-1521737604893-d14cc237f11d','media_type':'image','category':'socialmedia'},
    {'post_id':'post_112','name':'Brand Voice','caption':'Consistent branding across social channels. #branding','media_url':'https://images.unsplash.com/photo-1522202176988-66273c2fd55f','media_type':'image','category':'socialmedia'},
    {'post_id':'post_113','name':'Live Streaming','caption':'Connecting with audiences in real time. #livestream','media_url':'https://images.unsplash.com/photo-1551817958-20204d6ab93c','media_type':'image','category':'socialmedia'},
    {'post_id':'post_114','name':'Analytics Pro','caption':'Tracking performance and engagement metrics. #analytics','media_url':'https://images.unsplash.com/photo-1551288049-bebda4e38f71','media_type':'image','category':'socialmedia'},
    {'post_id':'post_115','name':'Social Strategy','caption':'Planning content that converts followers. #strategy','media_url':'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4','media_type':'image','category':'socialmedia'},
    {'post_id':'post_116','name':'Food Lover','caption':'Delicious meals made with passion. #foodie','media_url':'https://images.unsplash.com/photo-1504674900247-0877df9cc836','media_type':'image','category':'food'},
    {'post_id':'post_117','name':'Chef Specials','caption':'Plating dishes like a piece of art. #chef','media_url':'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe','media_type':'image','category':'food'},
    {'post_id':'post_118','name':'Street Food','caption':'Bold flavors from street food culture. #streetfood','media_url':'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0','media_type':'image','category':'food'},
    {'post_id':'post_119','name':'Healthy Eats 2','caption':'Nutritious meals that fuel the body. #healthyfood','media_url':'https://images.unsplash.com/photo-1490645935967-10de6ba17061','media_type':'image','category':'food'},
    {'post_id':'post_120','name':'Dessert Time','caption':'Sweet treats for every craving. #dessert','media_url':'https://images.unsplash.com/photo-1551024601-bec78aea704b','media_type':'image','category':'food'},
    {'post_id':'post_121','name':'Coffee Break','caption':'Great coffee makes great days. #coffee','media_url':'https://images.unsplash.com/photo-1509042239860-f550ce710b93','media_type':'image','category':'food'},
    {'post_id':'post_122','name':'Home Cooking','caption':'Comfort food made at home. #homecooking','media_url':'https://images.unsplash.com/photo-1512058564366-c9e3e0464b6c','media_type':'image','category':'food'},
    {'post_id':'post_123','name':'Vegan Kitchen','caption':'Plant-based meals packed with flavor. #vegan','media_url':'https://images.unsplash.com/photo-1498579809087-ef1e558fd1da','media_type':'image','category':'food'},
    {'post_id':'post_124','name':'Food Photography','caption':'Capturing food at its most delicious. #foodphotography','media_url':'https://images.unsplash.com/photo-1476224203421-9ac39bcb3327','media_type':'image','category':'food'},
    {'post_id':'post_125','name':'Global Cuisine','caption':'Exploring flavors from around the world. #cuisine','media_url':'https://images.unsplash.com/photo-1499028344343-cd173ffc68a9','media_type':'image','category':'food'},
    {'post_id':'post_126','name':'Game Night','caption':'Intense match and unforgettable moments. #sports','media_url':'https://images.unsplash.com/photo-1502877338535-766e1452684a','media_type':'image','category':'sports'},
    {'post_id':'post_127','name':'Football Arena','caption':'Where legends are made on the field. #football','media_url':'https://images.unsplash.com/photo-1508098682722-e99c43a406b2','media_type':'image','category':'sports'},
    {'post_id':'post_128','name':'Basketball Court','caption':'Fast breaks and buzzer beaters. #basketball','media_url':'https://images.unsplash.com/photo-1546519638-68e109498ffc','media_type':'image','category':'sports'},
    {'post_id':'post_129','name':'Cricket Fever','caption':'Every run counts in this thrilling game. #cricket','media_url':'https://images.unsplash.com/photo-1593766788306-28561086694e','media_type':'image','category':'sports'},
    {'post_id':'post_130','name':'Tennis Match','caption':'Precision, power, and focus on court. #tennis','media_url':'https://images.unsplash.com/photo-1521412644187-c49fa049e84d','media_type':'image','category':'sports'},
    {'post_id':'post_131','name':'Esports Zone','caption':'Competitive gaming at the highest level. #esports','media_url':'https://images.unsplash.com/photo-1542751371-adc38448a05e','media_type':'image','category':'sports'},
    {'post_id':'post_132','name':'Athlete Life','caption':'Training hard to perform harder. #athlete','media_url':'https://images.unsplash.com/photo-1521412644187-c49fa049e84d','media_type':'image','category':'sports'},
    {'post_id':'post_133','name':'Stadium Vibes','caption':'The energy of a packed stadium. #gameday','media_url':'https://images.unsplash.com/photo-1505842465776-3b4953ca4f0c','media_type':'image','category':'sports'},
    {'post_id':'post_134','name':'Fitness Sports','caption':'Strength and stamina define the game. #fitness','media_url':'https://images.unsplash.com/photo-1558611848-73f7eb4001a1','media_type':'image','category':'sports'},
    {'post_id':'post_135','name':'Victory Moment','caption':'Celebrating the win after hard work. #champions','media_url':'https://images.unsplash.com/photo-1517649763962-0c623066013b','media_type':'image','category':'sports'},
    {'post_id':'post_136','name':'Finance Daily','caption':'Managing money with smarter strategies. #finance','media_url':'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c','media_type':'image','category':'finance'},
    {'post_id':'post_137','name':'Stock Market','caption':'Tracking trends in the stock market. #stocks','media_url':'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3','media_type':'image','category':'finance'},
    {'post_id':'post_138','name':'Investment Hub','caption':'Investing for long-term growth. #investing','media_url':'https://images.unsplash.com/photo-1569025690938-a00729c9e1f9','media_type':'image','category':'finance'},
    {'post_id':'post_139','name':'Crypto Finance','caption':'Digital assets shaping modern finance. #crypto','media_url':'https://images.unsplash.com/photo-1621416894569-0f39ed31d247','media_type':'image','category':'finance'},
    {'post_id':'post_140','name':'Personal Finance','caption':'Budgeting today for a better tomorrow. #money','media_url':'https://images.unsplash.com/photo-1554224154-22dec7ec8818','media_type':'image','category':'finance'},
    {'post_id':'post_141','name':'FinTech World','caption':'Technology transforming financial services. #fintech','media_url':'https://images.unsplash.com/photo-1556741533-f6acd647d2fb','media_type':'image','category':'finance'},
    {'post_id':'post_142','name':'Wealth Planning','caption':'Planning wealth with purpose and clarity. #wealth','media_url':'https://images.unsplash.com/photo-1605902711622-cfb43c4437d1','media_type':'image','category':'finance'},
    {'post_id':'post_143','name':'Market Analysis','caption':'Analyzing data for smarter decisions. #market','media_url':'https://images.unsplash.com/photo-1551288049-bebda4e38f71','media_type':'image','category':'finance'},
    {'post_id':'post_144','name':'Startup Finance','caption':'Funding ideas that change the world. #startup','media_url':'https://images.unsplash.com/photo-1520607162513-77705c0f0d4a','media_type':'image','category':'finance'},
    {'post_id':'post_145','name':'Global Economy','caption':'Understanding global financial movements. #economy','media_url':'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e','media_type':'image','category':'finance'},
    {'post_id':'post_146','name':'Movie Night','caption':'Lights, camera, action. #movies','media_url':'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba','media_type':'image','category':'movies'},
    {'post_id':'post_147','name':'Cinema World','caption':'The magic of storytelling on screen. #cinema','media_url':'https://images.unsplash.com/photo-1517602302552-471fe67acf66','media_type':'image','category':'movies'},
    {'post_id':'post_148','name':'Film Studio','caption':'Behind the scenes of filmmaking. #filmmaking','media_url':'https://images.unsplash.com/photo-1505685296765-3a2736de412f','media_type':'image','category':'movies'},
    {'post_id':'post_149','name':'Directors Cut','caption':'Creative vision brought to life. #director','media_url':'https://images.unsplash.com/photo-1497032628192-86f99bcd76bc','media_type':'image','category':'movies'},
    {'post_id':'post_150','name':'Blockbuster','caption':'Big screens and bigger stories. #blockbuster','media_url':'https://images.unsplash.com/photo-1542204165-65bf26472b9b','media_type':'image','category':'movies'},
    {'post_id':'post_151','name':'Indie Films','caption':'Independent cinema with heart. #indiefilm','media_url':'https://images.unsplash.com/photo-1517602302552-471fe67acf66','media_type':'image','category':'movies'},
    {'post_id':'post_152','name':'Movie Review','caption':'Breaking down the latest releases. #moviereview','media_url':'https://images.unsplash.com/photo-1598899134739-fc08f55a5316','media_type':'image','category':'movies'},
    {'post_id':'post_153','name':'Classic Films','caption':'Timeless classics that never fade. #classicmovies','media_url':'https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9','media_type':'image','category':'movies'},
    {'post_id':'post_154','name':'Movie Buff','caption':'Watching films is a lifestyle. #moviebuff','media_url':'https://images.unsplash.com/photo-1505685296765-3a2736de412f','media_type':'image','category':'movies'},
    {'post_id':'post_155','name':'Film Festival','caption':'Celebrating cinema from around the world. #filmfestival','media_url':'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91','media_type':'image','category':'movies'},
    {'post_id':'post_156','name':'Music Vibes','caption':'Music that sets the mood. #music','media_url':'https://images.unsplash.com/photo-1511379938547-c1f69419868d','media_type':'image','category':'music'},
    {'post_id':'post_157','name':'Live Concert','caption':'Nothing beats live music energy. #concert','media_url':'https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2','media_type':'image','category':'music'},
    {'post_id':'post_158','name':'Studio Session','caption':'Creating sounds that tell stories. #musicstudio','media_url':'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4','media_type':'image','category':'music'},
    {'post_id':'post_159','name':'Singer Life','caption':'Expressing emotions through vocals. #singer','media_url':'https://images.unsplash.com/photo-1516280440614-37939bbacd81','media_type':'image','category':'music'},
    {'post_id':'post_160','name':'Guitar Sessions','caption':'Strings, rhythm, and soul. #guitar','media_url':'https://images.unsplash.com/photo-1510915361894-db8b60106cb1','media_type':'image','category':'music'},
    {'post_id':'post_161','name':'DJ Night','caption':'Spinning tracks that move the crowd. #DJ','media_url':'https://images.unsplash.com/photo-1518972559570-7cc1309f3229','media_type':'image','category':'music'},
    {'post_id':'post_162','name':'Music Producer','caption':'Crafting beats behind the scenes. #producer','media_url':'https://images.unsplash.com/photo-1497032205916-ac775f0649ae','media_type':'image','category':'music'},
    {'post_id':'post_163','name':'Headphones On','caption':'Lost in the music. #nowplaying','media_url':'https://images.unsplash.com/photo-1505740420928-5e560c06d30e','media_type':'image','category':'music'},
    {'post_id':'post_164','name':'Band Life','caption':'Band practice before the big show. #bandlife','media_url':'https://images.unsplash.com/photo-1506157786151-b8491531f063','media_type':'image','category':'music'},
    {'post_id':'post_165','name':'Music Festival','caption':'Where music and memories collide. #musicfestival','media_url':'https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2','media_type':'image','category':'music'},
    {'post_id':'post_166','name':'Learning Hub','caption':'Education opens doors to endless opportunities. #education','media_url':'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f','media_type':'image','category':'education'},
    {'post_id':'post_167','name':'Classroom Life','caption':'Where curiosity meets knowledge. #classroom','media_url':'https://images.unsplash.com/photo-1503676260728-1c00da094a0b','media_type':'image','category':'education'},
    {'post_id':'post_168','name':'Online Learning','caption':'Learning anytime, anywhere through digital platforms. #onlinelearning','media_url':'https://images.unsplash.com/photo-1584697964403-0c2b35f7b3f4','media_type':'image','category':'education'},
    {'post_id':'post_169','name':'Student Life','caption':'Balancing studies, dreams, and growth. #studentlife','media_url':'https://images.unsplash.com/photo-1523050854058-8df90110c9f1','media_type':'image','category':'education'},
    {'post_id':'post_170','name':'Teachers Desk','caption':'Educators shaping the future every day. #teachers','media_url':'https://images.unsplash.com/photo-1513258496099-48168024aec0','media_type':'image','category':'education'},
    {'post_id':'post_171','name':'Study Time','caption':'Focused study leads to real progress. #studymotivation','media_url':'https://images.unsplash.com/photo-1519682337058-a94d519337bc','media_type':'image','category':'education'},
    {'post_id':'post_172','name':'Graduation Day','caption':'Celebrating milestones and achievements. #graduation','media_url':'https://images.unsplash.com/photo-1523580846011-d3a5bc25702b','media_type':'image','category':'education'},
    {'post_id':'post_173','name':'Skill Building','caption':'Developing skills for the future workforce. #skills','media_url':'https://images.unsplash.com/photo-1529070538774-1843cb3265df','media_type':'image','category':'education'},
    {'post_id':'post_174','name':'Library Study','caption':'Quiet spaces for deep learning. #library','media_url':'https://images.unsplash.com/photo-1507842217343-583bb7270b66','media_type':'image','category':'education'},
    {'post_id':'post_175','name':'Future Scholars','caption':'Inspiring minds to think beyond limits. #learning','media_url':'https://images.unsplash.com/photo-1509062522246-3755977927d7','media_type':'image','category':'education'},
    {'post_id':'post_176','name':'Nature Views','caption':'Peaceful landscapes that calm the soul. #nature','media_url':'https://images.unsplash.com/photo-1501785888041-af3ef285b470','media_type':'image','category':'nature'},
    {'post_id':'post_177','name':'Mountain Escape','caption':'Breathtaking mountain views and fresh air. #mountains','media_url':'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee','media_type':'image','category':'nature'},
    {'post_id':'post_178','name':'Forest Walk','caption':'Finding peace among the trees. #forest','media_url':'https://images.unsplash.com/photo-1441974231531-c6227db76b6e','media_type':'image','category':'nature'},
    {'post_id':'post_179','name':'Ocean Breeze','caption':'Waves, wind, and endless blue. #ocean','media_url':'https://images.unsplash.com/photo-1507525428034-b723cf961d3e','media_type':'image','category':'nature'},
    {'post_id':'post_180','name':'Sunset Moments','caption':'Golden sunsets painting the sky. #sunset','media_url':'https://images.unsplash.com/photo-1501973801540-537f08ccae7b','media_type':'image','category':'nature'},
    {'post_id':'post_181','name':'Wildlife Watch','caption':'Observing wildlife in their natural habitat. #wildlife','media_url':'https://images.unsplash.com/photo-1508672019048-805c876b67e2','media_type':'image','category':'nature'},
    {'post_id':'post_182','name':'Green Earth','caption':'Protecting nature for future generations. #environment','media_url':'https://images.unsplash.com/photo-1469474968028-56623f02e42e','media_type':'image','category':'nature'},
    {'post_id':'post_183','name':'Waterfall Trails','caption':'Nature beauty flowing freely. #waterfall','media_url':'https://images.unsplash.com/photo-1502082553048-f009c37129b9','media_type':'image','category':'nature'},
    {'post_id':'post_184','name':'Desert Calm','caption':'Finding beauty in vast desert landscapes. #desert','media_url':'https://images.unsplash.com/photo-1500534314209-a26db0f5a2c3','media_type':'image','category':'nature'},
    {'post_id':'post_185','name':'Nature Photography','caption':'Capturing the raw beauty of nature. #naturephotography','media_url':'https://images.unsplash.com/photo-1470770841072-f978cf4d019e','media_type':'image','category':'nature'},
    {'post_id':'post_186','name':'Market Trends','caption':'Tracking the ups and downs of the stock market. #stocks','media_url':'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3','media_type':'image','category':'stocks'},
    {'post_id':'post_187','name':'Trading Desk','caption':'Decisions made here can change portfolios. #trading','media_url':'https://images.unsplash.com/photo-1559526324-593bc073d938','media_type':'image','category':'stocks'},
    {'post_id':'post_188','name':'Stock Analysis','caption':'Data-driven insights for smarter investments. #analysis','media_url':'https://images.unsplash.com/photo-1551288049-bebda4e38f71','media_type':'image','category':'stocks'},
    {'post_id':'post_189','name':'Bull Market','caption':'Celebrating the highs of the market. #bullmarket','media_url':'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3','media_type':'image','category':'stocks'},
    {'post_id':'post_190','name':'Bear Market','caption':'Navigating the lows with strategy. #bearmarket','media_url':'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c','media_type':'image','category':'stocks'},
    {'post_id':'post_191','name':'Investors Hub','caption':'Where investors meet insights. #investment','media_url':'https://images.unsplash.com/photo-1569025690938-a00729c9e1f9','media_type':'image','category':'stocks'},
    {'post_id':'post_192','name':'Trading Screen','caption':'Charts, numbers, and quick decisions. #tradingdesk','media_url':'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3','media_type':'image','category':'stocks'},
    {'post_id':'post_193','name':'Financial Growth','caption':'Strategies to grow your portfolio. #finance','media_url':'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c','media_type':'image','category':'stocks'},
    {'post_id':'post_194','name':'Market Watch','caption':'Keeping an eye on global trends. #marketwatch','media_url':'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3','media_type':'image','category':'stocks'},
    {'post_id':'post_195','name':'Trading Floor','caption':'The pulse of the stock exchange. #tradingfloor','media_url':'https://images.unsplash.com/photo-1559526324-593bc073d938','media_type':'image','category':'stocks'},
    {'post_id':'post_196','name':'Luxury Cars','caption':'Exquisite designs and performance on wheels. #luxurycars','media_url':'https://images.unsplash.com/photo-1503376780353-7e6692767b70','media_type':'image','category':'vehicles'},
    {'post_id':'post_197','name':'Motorcycle Ride','caption':'Freedom on two wheels. #motorcycle','media_url':'https://images.unsplash.com/photo-1504215680853-026ed2a45def','media_type':'image','category':'vehicles'},
    {'post_id':'post_198','name':'Sports Car','caption':'Speed, style, and adrenaline. #sportscar','media_url':'https://images.unsplash.com/photo-1511919884226-fd3cad34687c','media_type':'image','category':'vehicles'},
    {'post_id':'post_199','name':'Vintage Ride','caption':'Classic cars with timeless charm. #vintagecars','media_url':'https://images.unsplash.com/photo-1502877338535-766e1452684a','media_type':'image','category':'vehicles'},
    {'post_id':'post_200','name':'Electric Vehicles','caption':'Driving towards a sustainable future. #EV','media_url':'https://images.unsplash.com/photo-1606813902864-93b3d6dfe8f0','media_type':'image','category':'vehicles'},
    {'post_id':'post_201','name':'Offroad Adventure','caption':'Exploring the unbeaten path. #offroad','media_url':'https://images.unsplash.com/photo-1587401991296-0e7db86ff8de','media_type':'image','category':'vehicles'},
    {'post_id':'post_202','name':'Truck Life','caption':'Powerful and dependable. #trucks','media_url':'https://images.unsplash.com/photo-1504215680853-026ed2a45def','media_type':'image','category':'vehicles'},
    {'post_id':'post_203','name':'Car Interior','caption':'Design meets comfort. #carinterior','media_url':'https://images.unsplash.com/photo-1525609004556-c46c7d6cf023','media_type':'image','category':'vehicles'},
    {'post_id':'post_204','name':'Road Trip Car','caption':'The journey matters more than the destination. #roadtrip','media_url':'https://images.unsplash.com/photo-1502877338535-766e1452684a','media_type':'image','category':'vehicles'},
    {'post_id':'post_205','name':'Car Showroom','caption':'Exploring the latest models and innovations. #carshowroom','media_url':'https://images.unsplash.com/photo-1511919884226-fd3cad34687c','media_type':'image','category':'vehicles'},
    {'post_id':'post_206','name':'Cozy Cafe','caption':'Warm vibes and aromatic coffee. #cafe','media_url':'https://images.unsplash.com/photo-1529070538774-1843cb3265df','media_type':'image','category':'cafes'},
    {'post_id':'post_207','name':'Coffee Art','caption':'Latte designs that make mornings better. #coffeeart','media_url':'https://images.unsplash.com/photo-1511920170033-f8396924c348','media_type':'image','category':'cafes'},
    {'post_id':'post_208','name':'Urban Cafe','caption':'Trendy cafes in the heart of the city. #urbancafe','media_url':'https://images.unsplash.com/photo-1509042239860-f550ce710b93','media_type':'image','category':'cafes'},
    {'post_id':'post_209','name':'Outdoor Cafe','caption':'Enjoying coffee with a view. #outdoorcafe','media_url':'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4','media_type':'image','category':'cafes'},
    {'post_id':'post_210','name':'Cafe Vibes','caption':'Music, coffee, and relaxation. #cafemood','media_url':'https://images.unsplash.com/photo-1470337458703-46ad1756a187','media_type':'image','category':'cafes'},
    {'post_id':'post_211','name':'Pastry and Coffee','caption':'Delicious treats paired with your favorite brew. #coffeeandpastry','media_url':'https://images.unsplash.com/photo-1505250469679-203ad9ced0cb','media_type':'image','category':'cafes'},
    {'post_id':'post_212','name':'Evening Cafe','caption':'Twilight and coffee moments. #eveningcafe','media_url':'https://images.unsplash.com/photo-1470336120461-9e42b9b9c3d6','media_type':'image','category':'cafes'},
    {'post_id':'post_213','name':'Cafe Corner','caption':'A cozy nook for work or reading. #cafecorner','media_url':'https://images.unsplash.com/photo-1511920170033-f8396924c348','media_type':'image','category':'cafes'},
    {'post_id':'post_214','name':'Morning Brew','caption':'Start your day with fresh coffee. #morningcoffee','media_url':'https://images.unsplash.com/photo-1509042239860-f550ce710b93','media_type':'image','category':'cafes'},
    {'post_id':'post_215','name':'Coffee Culture','caption':'Exploring cafes from around the world. #coffeeculture','media_url':'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4','media_type':'image','category':'cafes'},
]

# qdrant seeding 
def seed():
    print(f"\nChecking embedding service at {EMBEDDING_SERVICE_URL}...")
    try:
        r = requests.get(f"{EMBEDDING_SERVICE_URL}/health", timeout=5)
        print(f"Embedding service OK: {r.json()}")
    except Exception as e:
        print(f"embedding service not reachable: {e}")
        print("   Make sure embedding_service.py is running first!")
        sys.exit(1)
    test_emb = get_embedding("test")
    dim = len(test_emb)
    print(f"✓ Embedding dim: {dim}")

    ensure_collection(dim)

    print(f"\nSeeding {len(sample_posts)} posts to Qdrant...\n")
    success = 0
    failed  = 0

    for post in sample_posts:
        try:
            post_num = int(post['post_id'].replace('post_', ''))
            text     = f"{post['name']}: {post['caption']}"
            embedding = get_embedding(text)

            qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=[PointStruct(
                    id=post_num,
                    vector=embedding,
                    payload={
                        'post_id':    post['post_id'],
                        'name':       post['name'],
                        'caption':    post['caption'],
                        'media_url':  post['media_url'],
                        'media_type': post['media_type'],
                        'category':   post['category'],
                        'created_at': datetime.utcnow().isoformat(),
                    }
                )]
            )
            print(f"{post['post_id']} [{post['category']}] — {post['name']}")
            success += 1
        except Exception as e:
            print(f"{post['post_id']} FAILED: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Done {success} seeded  {failed} failed")
    print(f"Total in Qdrant: {qdrant.get_collection(COLLECTION_NAME).points_count}")

if __name__ == '__main__':
    seed()