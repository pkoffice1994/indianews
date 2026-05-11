"""
Management command: python manage.py add_news
Adds 10 bilingual (Hindi + English) news articles with categories.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from news.models import News, Category, ShortNews, Tag
from django.utils.text import slugify
import uuid


NEWS_DATA = [
    {
        "title_hi": "भारत-पाकिस्तान तनाव: सीमा पर सेना हाई अलर्ट पर, PM मोदी ने की अहम बैठक",
        "title_en": "India-Pakistan Tension: Army on High Alert at Border, PM Modi Holds Key Meeting",
        "summary_hi": "भारत-पाकिस्तान के बीच बढ़ते तनाव के बीच सरकार ने राष्ट्रीय सुरक्षा पर उच्च स्तरीय बैठक बुलाई।",
        "summary_en": "Amid escalating India-Pakistan tensions, the government convened a high-level national security meeting.",
        "content_hi": """नई दिल्ली। भारत-पाकिस्तान के बीच तनाव चरम पर पहुंच गया है। प्रधानमंत्री नरेंद्र मोदी ने राष्ट्रीय सुरक्षा सलाहकार अजीत डोभाल और तीनों सेना प्रमुखों के साथ आपात बैठक की।

सीमा पर भारतीय सेना को हाई अलर्ट पर रखा गया है। वायुसेना के लड़ाकू विमान सतर्क हैं और नौसेना अरब सागर में तैयार है।

रक्षा मंत्री राजनाथ सिंह ने कहा कि भारत किसी भी चुनौती का सामना करने में सक्षम है। देश की संप्रभुता और अखंडता की रक्षा हर हाल में की जाएगी।

विपक्ष ने भी इस मामले में सरकार को पूर्ण समर्थन देने का आश्वासन दिया है। देश एकजुट होकर किसी भी खतरे का मुकाबला करने के लिए तैयार है।

अमेरिका और रूस सहित कई देशों ने दोनों पक्षों से संयम बरतने की अपील की है।""",
        "content_en": """New Delhi. Tensions between India and Pakistan have reached a peak. Prime Minister Narendra Modi held an emergency meeting with National Security Advisor Ajit Doval and the chiefs of all three armed forces.

The Indian Army has been placed on high alert along the border. Air Force fighter jets are on standby and the Navy is positioned in the Arabian Sea.

Defence Minister Rajnath Singh stated that India is capable of meeting any challenge. The sovereignty and integrity of the nation will be protected at all costs.

The opposition also assured the government of full support in this matter. The country stands united and is ready to counter any threat.

Several countries including the US and Russia have appealed to both sides to exercise restraint.""",
        "category_slug": "desh",
        "is_breaking": True, "is_featured": True, "is_top_story": True,
        "image": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&q=80",
    },
    {
        "title_hi": "IPL 2026 फाइनल: मुंबई इंडियंस ने चेन्नई को हराकर जीती ट्रॉफी, रोहित का शतक",
        "title_en": "IPL 2026 Final: Mumbai Indians Beat Chennai to Win Trophy, Rohit's Century",
        "summary_hi": "रोमांचक फाइनल में मुंबई इंडियंस ने चेन्नई सुपर किंग्स को 8 विकेट से हराया।",
        "summary_en": "In a thrilling final, Mumbai Indians defeated Chennai Super Kings by 8 wickets.",
        "content_hi": """मुंबई। IPL 2026 का रोमांचक सफर आखिरकार मुंबई इंडियंस की जीत के साथ समाप्त हुआ। वानखेड़े स्टेडियम में खेले गए फाइनल में मुंबई ने चेन्नई सुपर किंग्स को 8 विकेट से हराया।

रोहित शर्मा ने शानदार 104 रन की पारी खेली। उन्होंने मात्र 58 गेंदों में यह शतक पूरा किया। इसके साथ ही वे IPL इतिहास के सबसे सफल कप्तान बन गए।

चेन्नई ने पहले बल्लेबाजी करते हुए 185 रन बनाए। मुंबई ने यह लक्ष्य 16.4 ओवर में हासिल कर लिया।

एमएस धोनी ने अपने करियर के आखिरी IPL मैच में 62 रन बनाए। पूरे स्टेडियम ने उनके लिए खड़े होकर तालियां बजाईं।

मुंबई इंडियंस को 20 करोड़ रुपये की पुरस्कार राशि मिली।""",
        "content_en": """Mumbai. The thrilling IPL 2026 journey finally concluded with Mumbai Indians' victory. In the final played at Wankhede Stadium, Mumbai defeated Chennai Super Kings by 8 wickets.

Rohit Sharma played a brilliant innings of 104 runs. He completed this century in just 58 balls, becoming the most successful captain in IPL history.

Chennai batted first and scored 185 runs. Mumbai achieved this target in 16.4 overs.

MS Dhoni scored 62 runs in what may be his final IPL match. The entire stadium gave him a standing ovation.

Mumbai Indians received a prize money of Rs 20 crore.""",
        "category_slug": "khel",
        "is_breaking": True, "is_featured": True,
        "image": "https://images.unsplash.com/photo-1540747913346-19212a4cf528?w=1200&q=80",
    },
    {
        "title_hi": "बजट 2026: मध्यम वर्ग को राहत, 12 लाख तक की आय पर शून्य टैक्स",
        "title_en": "Budget 2026: Relief for Middle Class, Zero Tax on Income Up to Rs 12 Lakh",
        "summary_hi": "वित्त मंत्री निर्मला सीतारमण ने बजट में मध्यम वर्ग को बड़ी राहत दी।",
        "summary_en": "Finance Minister Nirmala Sitharaman provided major relief to the middle class in the budget.",
        "content_hi": """नई दिल्ली। वित्त मंत्री निर्मला सीतारमण ने संसद में बजट 2026-27 पेश किया। इस बार 12 लाख रुपये तक की सालाना आय पर कोई इनकम टैक्स नहीं लगेगा।

नई टैक्स व्यवस्था के तहत स्लैब को पूरी तरह बदला गया है। 12 से 15 लाख पर 5%, 15 से 20 लाख पर 10% और 20 लाख से ऊपर पर 20% टैक्स होगा।

किसानों के लिए पीएम किसान सम्मान निधि को 6,000 से बढ़ाकर 8,000 रुपये प्रति वर्ष किया गया।

स्वास्थ्य क्षेत्र के लिए 2.5 लाख करोड़ का प्रावधान किया गया। हर जिले में एक AIIMS खोलने की घोषणा की गई।

रेलवे को 3.5 लाख करोड़ रुपये का बजट दिया गया। 100 नए वंदे भारत ट्रेनें चलाई जाएंगी।""",
        "content_en": """New Delhi. Finance Minister Nirmala Sitharaman presented Budget 2026-27 in Parliament. This time, there will be no income tax on annual income up to Rs 12 lakh.

Under the new tax regime, the slabs have been completely revised. 5% tax on Rs 12-15 lakh, 10% on Rs 15-20 lakh, and 20% above Rs 20 lakh.

PM Kisan Samman Nidhi for farmers increased from Rs 6,000 to Rs 8,000 per year.

Rs 2.5 lakh crore allocated for the health sector. One AIIMS to be opened in every district.

Railways given a budget of Rs 3.5 lakh crore. 100 new Vande Bharat trains to be launched.""",
        "category_slug": "vyapaar",
        "is_breaking": False, "is_featured": True,
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80",
    },
    {
        "title_hi": "ISRO का ऐतिहासिक मिशन: चंद्रमा से मिट्टी लेकर लौटा चंद्रयान-4",
        "title_en": "ISRO Historic Mission: Chandrayaan-4 Returns with Moon Soil Samples",
        "summary_hi": "भारत के चंद्रयान-4 ने इतिहास रचा, चंद्रमा की सतह से मिट्टी के नमूने लेकर सफलतापूर्वक वापस आया।",
        "summary_en": "India's Chandrayaan-4 made history by successfully returning with soil samples from the lunar surface.",
        "content_hi": """बेंगलुरु। भारतीय अंतरिक्ष अनुसंधान संगठन (ISRO) ने एक और ऐतिहासिक उपलब्धि हासिल की। चंद्रयान-4 चंद्रमा की सतह से 2.5 किलोग्राम मिट्टी के नमूने लेकर सफलतापूर्वक पृथ्वी पर लौट आया।

यह भारत का पहला sample return mission था। इससे पहले केवल अमेरिका, रूस और चीन ही यह कारनामा कर पाए थे।

ISRO प्रमुख डॉ. वी. नारायणन ने कहा कि यह भारत के अंतरिक्ष कार्यक्रम की सबसे बड़ी सफलता है।

प्रधानमंत्री मोदी ने ISRO की पूरी टीम को बधाई दी। उन्होंने कहा कि यह 140 करोड़ भारतीयों की उपलब्धि है।

चंद्रमा के नमूनों का अध्ययन अगले 2 साल तक किया जाएगा। इससे चंद्रमा की उत्पत्ति के बारे में नई जानकारी मिलेगी।""",
        "content_en": """Bengaluru. The Indian Space Research Organisation (ISRO) achieved another historic milestone. Chandrayaan-4 successfully returned to Earth carrying 2.5 kg of soil samples from the lunar surface.

This was India's first sample return mission. Previously, only the US, Russia and China had accomplished this feat.

ISRO Chief Dr. V. Narayanan said this is the greatest success of India's space programme.

PM Modi congratulated the entire ISRO team, saying it was an achievement of 140 crore Indians.

The lunar samples will be studied for the next 2 years. This will provide new information about the origin of the Moon.""",
        "category_slug": "takneek",
        "is_breaking": True, "is_featured": True,
        "image": "https://images.unsplash.com/photo-1517976487492-5750f3195933?w=1200&q=80",
    },
    {
        "title_hi": "सुप्रीम कोर्ट का बड़ा फैसला: NEET परीक्षा में OBC आरक्षण 27% रहेगा",
        "title_en": "Supreme Court Big Verdict: OBC Reservation in NEET Exam to Remain at 27%",
        "summary_hi": "सर्वोच्च न्यायालय ने NEET में ओबीसी आरक्षण को लेकर महत्वपूर्ण निर्णय सुनाया।",
        "summary_en": "The Supreme Court delivered an important decision regarding OBC reservation in NEET.",
        "content_hi": """नई दिल्ली। सुप्रीम कोर्ट ने मंगलवार को एक ऐतिहासिक फैसला सुनाया। कोर्ट ने NEET परीक्षा में OBC आरक्षण 27% बनाए रखने का आदेश दिया।

चीफ जस्टिस संजीव खन्ना की अध्यक्षता वाली पांच सदस्यीय संविधान पीठ ने यह फैसला 4:1 के बहुमत से सुनाया।

इस फैसले से लाखों ओबीसी छात्रों को फायदा होगा जो मेडिकल और इंजीनियरिंग में दाखिले की तैयारी कर रहे हैं।

केंद्र सरकार ने फैसले का स्वागत किया। सामाजिक न्याय मंत्री डॉ. वीरेंद्र कुमार ने कहा यह ओबीसी समाज की जीत है।

विपक्षी पार्टियों ने भी इस फैसले को ऐतिहासिक बताया है।""",
        "content_en": """New Delhi. The Supreme Court delivered a historic verdict on Tuesday. The court ordered that OBC reservation in NEET exam be maintained at 27%.

The five-member constitutional bench headed by Chief Justice Sanjiv Khanna delivered the verdict by a 4:1 majority.

This decision will benefit millions of OBC students preparing for admission to medical and engineering colleges.

The central government welcomed the verdict. Social Justice Minister Dr. Virendra Kumar said it is a victory for the OBC community.

Opposition parties also called the verdict historic.""",
        "category_slug": "desh",
        "is_breaking": False, "is_featured": True,
        "image": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200&q=80",
    },
    {
        "title_hi": "शेयर बाज़ार: सेंसेक्स 82,000 के पार, IT और बैंकिंग शेयरों में तूफानी तेज़ी",
        "title_en": "Stock Market: Sensex Crosses 82,000, IT and Banking Stocks Surge Dramatically",
        "summary_hi": "विदेशी निवेशकों की भारी खरीदारी से शेयर बाज़ार में जबरदस्त तेज़ी आई।",
        "summary_en": "Heavy foreign investor buying led to a massive surge in the stock market.",
        "content_hi": """मुंबई। भारतीय शेयर बाज़ार ने आज नया इतिहास रचा। BSE सेंसेक्स पहली बार 82,000 अंकों के पार पहुंचा। निफ्टी 50 भी 24,800 के ऊपर बंद हुआ।

TCS, Infosys और Wipro के शेयरों में 3-5% की जबरदस्त तेज़ी आई। HDFC Bank और ICICI Bank के शेयर भी नई ऊंचाई पर पहुंचे।

विदेशी संस्थागत निवेशकों (FII) ने एक ही दिन में 12,500 करोड़ रुपये के शेयर खरीदे। यह इस साल की सबसे बड़ी एकल दिन की खरीदारी है।

भारत की GDP वृद्धि दर 8.2% रहने की उम्मीद है। इससे निवेशकों का भरोसा बढ़ा है।

आर्थिक विशेषज्ञों का मानना है कि साल के अंत तक सेंसेक्स 90,000 तक पहुंच सकता है।""",
        "content_en": """Mumbai. Indian stock markets created new history today. The BSE Sensex crossed 82,000 points for the first time. Nifty 50 also closed above 24,800.

TCS, Infosys and Wipro shares surged 3-5%. HDFC Bank and ICICI Bank shares also reached new highs.

Foreign Institutional Investors (FIIs) bought shares worth Rs 12,500 crore in a single day — the biggest single-day purchase this year.

India's GDP growth rate is expected to be 8.2%, boosting investor confidence.

Economic experts believe the Sensex could reach 90,000 by end of year.""",
        "category_slug": "vyapaar",
        "is_breaking": False, "is_featured": False,
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80",
    },
    {
        "title_hi": "बॉलीवुड: सलमान खान की 'टाइगर 4' ने पहले दिन 150 करोड़ की कमाई का रिकॉर्ड तोड़ा",
        "title_en": "Bollywood: Salman Khan's 'Tiger 4' Breaks Record with Rs 150 Crore on Day 1",
        "summary_hi": "सलमान खान की बहुप्रतीक्षित फिल्म Tiger 4 ने पहले दिन बॉक्स ऑफिस पर धमाल मचाया।",
        "summary_en": "Salman Khan's highly anticipated film Tiger 4 made a massive impact on the box office on its first day.",
        "content_hi": """मुंबई। सलमान खान और कटरीना कैफ स्टारर 'Tiger 4' ने भारतीय सिनेमा में नया इतिहास रच दिया। फिल्म ने पहले दिन देशभर के सिनेमाघरों में 150 करोड़ रुपये की कमाई की।

यह किसी हिंदी फिल्म की पहले दिन की सबसे बड़ी कमाई है। इससे पहले यह रिकॉर्ड पठान के नाम था जिसने 106 करोड़ कमाए थे।

फिल्म 15,000 से ज़्यादा स्क्रीन पर रिलीज़ हुई है। दुबई, लंदन और न्यूयॉर्क में भी पहले दिन हाउसफुल रहे।

सलमान खान ने कहा कि दर्शकों का यह प्यार उनकी सबसे बड़ी ताकत है।

निर्देशक मनीष शर्मा ने 5 साल में यह फिल्म बनाई है। बताया जा रहा है कि फिल्म का बजट 350 करोड़ था।""",
        "content_en": """Mumbai. Tiger 4, starring Salman Khan and Katrina Kaif, has created new history in Indian cinema. The film earned Rs 150 crore on its first day across cinemas nationwide.

This is the biggest opening day collection for any Hindi film. Previously, this record was held by Pathaan which earned Rs 106 crore.

The film has released on more than 15,000 screens. Shows were housefull on day one in Dubai, London and New York as well.

Salman Khan said the audience's love is his greatest strength.

Director Manish Sharma made this film over 5 years with a reported budget of Rs 350 crore.""",
        "category_slug": "manoranjan",
        "is_breaking": False, "is_featured": True,
        "image": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80",
    },
    {
        "title_hi": "मानसून 2026: केरल में समय से पहले आया मानसून, दिल्ली में भी जल्द दस्तक देगा",
        "title_en": "Monsoon 2026: Monsoon Arrives Early in Kerala, Delhi Too Expected to Get It Soon",
        "summary_hi": "इस साल मानसून सामान्य से 10 दिन पहले केरल पहुंचा। मौसम विभाग ने अच्छी बारिश का अनुमान जताया।",
        "summary_en": "This year monsoon arrived in Kerala 10 days ahead of schedule. The Met department predicted good rainfall.",
        "content_hi": """नई दिल्ली। भारतीय मौसम विज्ञान विभाग (IMD) ने घोषणा की कि दक्षिण-पश्चिम मानसून इस साल समय से पहले केरल पहुंच गया है।

पिछले साल के मुकाबले इस बार मानसून 10 दिन पहले आया है। IMD ने इस साल 107% सामान्य बारिश का अनुमान लगाया है।

किसानों के लिए यह अच्छी खबर है। इस साल धान, कपास और दलहन की बुवाई का रकबा बढ़ने की उम्मीद है।

उत्तर भारत में 15 जून तक मानसून पहुंचने की संभावना है। दिल्ली में 20-25 जून के बीच मानसून आ सकता है।

हालांकि बाढ़ प्रभावित क्षेत्रों में अतिरिक्त सावधानी बरतने की जरूरत होगी।""",
        "content_en": """New Delhi. The India Meteorological Department (IMD) announced that the South-West Monsoon has arrived in Kerala ahead of schedule this year.

Monsoon arrived 10 days earlier than last year. IMD has forecast 107% of normal rainfall this year.

This is good news for farmers. This year's sowing area for paddy, cotton and pulses is expected to increase.

Monsoon is likely to reach North India by June 15. Delhi could get monsoon between June 20-25.

However, extra caution will be needed in flood-prone areas.""",
        "category_slug": "desh",
        "is_breaking": False, "is_featured": False,
        "image": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200&q=80",
    },
    {
        "title_hi": "स्वास्थ्य: AIIMS ने विकसित किया कैंसर का सस्ता इलाज, 90% मरीजों में दिखा असर",
        "title_en": "Health: AIIMS Develops Affordable Cancer Treatment, Effective in 90% of Patients",
        "summary_hi": "AIIMS दिल्ली के वैज्ञानिकों ने कैंसर के इलाज में क्रांतिकारी खोज की है।",
        "summary_en": "Scientists at AIIMS Delhi have made a revolutionary discovery in cancer treatment.",
        "content_hi": """नई दिल्ली। AIIMS दिल्ली के वैज्ञानिकों ने कैंसर के इलाज में एक क्रांतिकारी खोज की है। उन्होंने एक नई दवा विकसित की है जो ब्रेस्ट कैंसर और लंग कैंसर के 90% मरीजों में प्रभावी पाई गई।

इस दवा की कीमत मौजूदा कैंसर दवाओं से 10 गुना कम है। अभी एक महीने का इलाज 5 लाख रुपये से ज़्यादा का पड़ता है, यह दवा मात्र 50,000 रुपये में मिलेगी।

शोध दल के प्रमुख डॉ. रमेश चंद्र ने बताया कि यह दवा शरीर की प्रतिरोधक क्षमता को बढ़ाकर कैंसर कोशिकाओं को नष्ट करती है।

स्वास्थ्य मंत्री ने इस खोज को ऐतिहासिक बताया। अगले 6 महीने में यह दवा बाज़ार में उपलब्ध हो जाएगी।

WHO ने भी इस दवा को 'game changer' बताया है।""",
        "content_en": """New Delhi. Scientists at AIIMS Delhi have made a revolutionary discovery in cancer treatment. They have developed a new drug found to be effective in 90% of breast cancer and lung cancer patients.

The cost of this drug is 10 times less than existing cancer medications. While current monthly treatment costs over Rs 5 lakh, this drug will be available for just Rs 50,000.

Research team head Dr. Ramesh Chandra explained that the drug destroys cancer cells by boosting the body's immune system.

The Health Minister called this discovery historic. The drug will be available in the market within the next 6 months.

The WHO has also described this drug as a 'game changer'.""",
        "category_slug": "swasthya",
        "is_breaking": False, "is_featured": True,
        "image": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&q=80",
    },
    {
        "title_hi": "शिक्षा: CBSE बोर्ड रिजल्ट घोषित, 94.5% छात्र पास, लड़कियों ने मारी बाज़ी",
        "title_en": "Education: CBSE Board Result Declared, 94.5% Students Pass, Girls Outshine Boys",
        "summary_hi": "CBSE 12वीं बोर्ड का परिणाम घोषित, इस बार लड़कियों का पास प्रतिशत लड़कों से ज़्यादा।",
        "summary_en": "CBSE Class 12 board results declared; girls' pass percentage higher than boys this year.",
        "content_hi": """नई दिल्ली। केंद्रीय माध्यमिक शिक्षा बोर्ड (CBSE) ने 12वीं कक्षा के नतीजे घोषित कर दिए। इस साल 94.5% छात्र उत्तीर्ण हुए।

लड़कियों का पास प्रतिशत 96.2% रहा जबकि लड़कों का 92.8%। यह लगातार पांचवीं बार है जब लड़कियों ने बेहतर प्रदर्शन किया।

त्रिवेंद्रम की छात्रा आस्था पिल्लई ने 99.8% अंक लेकर देशभर में टॉप किया। उन्होंने पांचों विषयों में 99 से ज़्यादा नंबर लिए।

दिल्ली का पास प्रतिशत 97.3% रहा जो पिछले साल से 2% ज़्यादा है। राजस्थान में भी बेहतरीन नतीजे आए।

जो छात्र परिणाम से खुश नहीं हैं, वे 15 मई से 20 मई के बीच री-चेकिंग के लिए आवेदन कर सकते हैं।""",
        "content_en": """New Delhi. The Central Board of Secondary Education (CBSE) has declared the Class 12 results. This year 94.5% of students passed.

Girls' pass percentage stood at 96.2% while boys' was 92.8%. This is the fifth consecutive year girls have outperformed boys.

Aastha Pillai from Trivandrum topped the country with 99.8%, scoring above 99 in all five subjects.

Delhi's pass percentage was 97.3%, 2% higher than last year. Rajasthan also showed excellent results.

Students not satisfied with their results can apply for re-checking between May 15-20.""",
        "category_slug": "shiksha",
        "is_breaking": False, "is_featured": False,
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1200&q=80",
    },
]

SHORT_NEWS = [
    {"title": "पेट्रोल-डीजल के दाम: दिल्ली में पेट्रोल ₹94.77, डीजल ₹87.67 प्रति लीटर", "title_en": "Petrol-Diesel Prices: Delhi petrol ₹94.77, diesel ₹87.67 per litre", "video_url": "https://www.youtube.com/shorts/pA4SbsCP1Yg", "news_type": "video"},
    {"title": "सोने की कीमत: 10 ग्राम सोना ₹74,520, चांदी ₹89,400 प्रति किलो", "title_en": "Gold Price: 10g gold ₹74,520, silver ₹89,400 per kg"},
    {"title": "दिल्ली का मौसम: अधिकतम 38°C, न्यूनतम 24°C, आंशिक बादल", "title_en": "Delhi Weather: Max 38°C, Min 24°C, Partly Cloudy"},
    {"title": "डॉलर-रुपया: 1 डॉलर = ₹83.45, रुपया 10 पैसे मज़बूत हुआ", "title_en": "Dollar-Rupee: 1 USD = ₹83.45, Rupee strengthens by 10 paise"},
    {"title": "UPSC 2025 नतीजे: शक्ति दुबे बनीं IAS टॉपर, देशभर में जश्न", "title_en": "UPSC 2025 Results: Shakti Dubey becomes IAS topper, celebrations nationwide"},
    {"title": "विराट कोहली ने टेस्ट क्रिकेट से संन्यास लिया, BCCI ने दी विदाई", "title_en": "Virat Kohli retires from Test cricket, BCCI bids farewell"},
]


class Command(BaseCommand):
    help = 'Add 10 bilingual news articles to the database'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@indianews.in', 'admin123')
            self.stdout.write('Created admin user')

        # Ensure categories exist
        CATS = [
            ("देश",       "desh",       "India",         "#e60026"),
            ("राजनीति",   "rajneeti",   "Politics",      "#c0392b"),
            ("विश्व",     "vishwa",     "World",         "#2980b9"),
            ("खेल",       "khel",       "Sports",        "#27ae60"),
            ("व्यापार",   "vyapaar",    "Business",      "#f39c12"),
            ("तकनीक",     "takneek",    "Technology",    "#8e44ad"),
            ("मनोरंजन",   "manoranjan", "Entertainment", "#e67e22"),
            ("शिक्षा",    "shiksha",    "Education",     "#16a085"),
            ("स्वास्थ्य", "swasthya",   "Health",        "#e74c3c"),
            ("अपराध",     "apradh",     "Crime",         "#2c3e50"),
        ]
        for i, (name, slug, name_en, color) in enumerate(CATS):
            cat, created = Category.objects.get_or_create(slug=slug, defaults={
                'name': name, 'name_en': name_en, 'color': color,
                'show_in_nav': True, 'order': i, 'is_active': True
            })
            if not created:
                # Always update English name to correct value
                Category.objects.filter(slug=slug).update(name_en=name_en)

        created = 0
        for item in NEWS_DATA:
            cat = Category.objects.filter(slug=item['category_slug']).first()
            base_slug = slugify(item['title_en'][:80])
            if not base_slug:
                base_slug = str(uuid.uuid4())[:8]

            # Make slug unique
            final_slug = base_slug
            n = 1
            while News.objects.filter(slug=final_slug).exists():
                final_slug = f"{base_slug}-{n}"
                n += 1

            news = News.objects.create(
                title_hi=item['title_hi'],
                title_en=item['title_en'],
                summary_hi=item['summary_hi'],
                summary_en=item.get('summary_en', ''),
                content_hi=item['content_hi'],
                content_en=item.get('content_en', ''),
                category=cat,
                author=admin_user,
                status='published',
                is_breaking=item.get('is_breaking', False),
                is_featured=item.get('is_featured', False),
                is_top_story=item.get('is_top_story', False),
                featured_image_url=item.get('image', ''),
                slug=final_slug,
                published_at=timezone.now(),
            )
            self.stdout.write(f'  ✅ {news.title_hi[:50]}')
            created += 1

        # Add short news
        for sn in SHORT_NEWS:
            if not ShortNews.objects.filter(title=sn['title']).exists():
                ShortNews.objects.create(
                    title=sn['title'],
                    content=sn.get('title_en', ''),
                    video_url=sn.get('video_url', ''),
                    news_type=sn.get('news_type', 'text'),
                    is_active=True,
                )
            else:
                # Update video_url if provided
                if sn.get('video_url'):
                    ShortNews.objects.filter(title=sn['title']).update(
                        video_url=sn['video_url'],
                        news_type=sn.get('news_type', 'video'),
                    )

        # Add E-Paper with PDF URL
        import datetime
        from news.models import EPaper
        try:
            ep, ep_created = EPaper.objects.get_or_create(
                publish_date=datetime.date.today(),
                defaults={
                    'title': f"India News — {datetime.date.today().strftime('%d %B %Y')}",
                    'edition': 'Digital Edition',
                    'pdf_url': 'https://drive.google.com/file/d/1a9_pRRx5Vrg3FP3Th-b3f65ImOG-cPpD/preview',
                    'image_url': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
                    'is_active': True,
                }
            )
            # Always update PDF URL
            EPaper.objects.filter(pk=ep.pk).update(
                pdf_url='https://drive.google.com/file/d/1a9_pRRx5Vrg3FP3Th-b3f65ImOG-cPpD/preview',
                image_url='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
            )
            self.stdout.write(f'  📰 E-Paper: {ep.title}')
        except Exception as e:
            self.stdout.write(f'  ⚠️ EPaper error: {e}')
            # Try raw SQL as fallback
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO news_epaper 
                        (title, edition, pdf_file, pdf_url, image_url, publish_date, is_active, created_at)
                        VALUES (?, ?, '', ?, ?, ?, 1, datetime('now'))
                    """, [
                        f"India News — {datetime.date.today().strftime('%d %B %Y')}",
                        'Digital Edition',
                        'https://drive.google.com/file/d/1a9_pRRx5Vrg3FP3Th-b3f65ImOG-cPpD/preview',
                        'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
                        datetime.date.today().isoformat(),
                    ])
                    self.stdout.write('  📰 E-Paper added via SQL fallback')
                except Exception as e2:
                    self.stdout.write(f'  ❌ EPaper SQL fallback failed: {e2}')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Done! {created} news articles added successfully!'
        ))
