import { readFileSync, writeFileSync, readdirSync, statSync, mkdirSync, existsSync } from 'fs';
import { join, relative } from 'path';

const AFFILIATE_TAG = 'dailydealdarl-20';

const PRODUCT_MAP = {
  // Training Equipment
  'adjustable dumbbells': { asin: 'B001ARYU58', name: 'Bowflex SelectTech 552 Adjustable Dumbbells' },
  'adjustable dumbbell': { asin: 'B001ARYU58', name: 'Bowflex SelectTech 552' },
  'dumbbells': { asin: 'B001ARYU58', name: 'Bowflex SelectTech 552' },
  'dumbbell': { asin: 'B001ARYU58', name: 'Bowflex SelectTech 552' },
  'resistance bands': { asin: 'B01AVDVHTI', name: 'Fit Simplify Resistance Loop Exercise Bands' },
  'resistance band': { asin: 'B01AVDVHTI', name: 'Fit Simplify Resistance Loop Exercise Bands' },
  'pull up bar': { asin: 'B001EJMS6K', name: 'Iron Gym Pull Up Bar' },
  'pull-up bar': { asin: 'B001EJMS6K', name: 'Iron Gym Pull Up Bar' },
  'kettlebell': { asin: 'B003J9E5WO', name: 'CAP Barbell Cast Iron Kettlebell' },
  'kettlebells': { asin: 'B003J9E5WO', name: 'CAP Barbell Cast Iron Kettlebell' },
  'yoga mat': { asin: 'B01LP0VQYU', name: 'BalanceFrom All-Purpose Exercise Yoga Mat' },
  'exercise mat': { asin: 'B01LP0VQYU', name: 'BalanceFrom All-Purpose Exercise Yoga Mat' },
  'jump rope': { asin: 'B074NDHZY6', name: 'DEGOL Skipping Rope' },
  'ab roller': { asin: 'B010RB4TKE', name: 'VINSGUIR Ab Roller Wheel' },
  'weight bench': { asin: 'B07DNHR5PJ', name: 'FLYBIRD Adjustable Weight Bench' },
  'barbell': { asin: 'B001K4OPY2', name: 'CAP Barbell Olympic Bar' },
  'weight plates': { asin: 'B08P1CCRS7', name: 'Signature Fitness Olympic Bumper Plates' },
  'foam roller': { asin: 'B0040EKZDY', name: 'LuxFit Foam Roller' },
  'massage gun': { asin: 'B07MHBJYRH', name: 'Theragun Mini Percussion Massage Gun' },
  'power rack': { asin: 'B07BM2KWDB', name: 'Fitness Reality Power Rack' },
  'squat rack': { asin: 'B07BM2KWDB', name: 'Fitness Reality Power Rack' },
  'battle ropes': { asin: 'B00C2A9CLO', name: 'Profect Sports Battle Rope' },
  'weight vest': { asin: 'B07BBQVD4F', name: 'RunMax Weighted Vest' },
  'dip station': { asin: 'B002Y2SUU4', name: 'ProsourceFit Dip Stand Station' },
  'gym gloves': { asin: 'B074WN2KY5', name: 'Trideer Workout Gloves' },
  'lifting straps': { asin: 'B074WN2KY5', name: 'Trideer Workout Gloves' },
  'wrist wraps': { asin: 'B00ZFHEHCO', name: 'WOD Nation Wrist Wraps' },
  'knee sleeves': { asin: 'B019PS4SBA', name: 'Nordic Lifting Knee Sleeves' },
  'weightlifting belt': { asin: 'B00IAHFOXS', name: 'Dark Iron Fitness Leather Weight Lifting Belt' },
  'lifting belt': { asin: 'B00IAHFOXS', name: 'Dark Iron Fitness Leather Weight Lifting Belt' },
  'suspension trainer': { asin: 'B002YIA3CI', name: 'TRX GO Suspension Training System' },
  'trx': { asin: 'B002YIA3CI', name: 'TRX GO Suspension Training System' },
  'rowing machine': { asin: 'B078HGN5PL', name: 'Concept2 Model D Indoor Rowing Machine' },
  'stationary bike': { asin: 'B08FDKZFWZ', name: 'Schwinn Fitness Indoor Cycling Bike' },
  'exercise bike': { asin: 'B08FDKZFWZ', name: 'Schwinn Fitness Indoor Cycling Bike' },
  'treadmill': { asin: 'B08DFPZV2T', name: 'NordicTrack T Series Treadmill' },
  'pull up': { asin: 'B001EJMS6K', name: 'Iron Gym Pull Up Bar' },
  'push up': { asin: 'B00OB74AH6', name: 'Perfect Fitness Push Up Elite' },
  'push-up': { asin: 'B00OB74AH6', name: 'Perfect Fitness Push Up Elite' },
  'pushup': { asin: 'B00OB74AH6', name: 'Perfect Fitness Push Up Elite' },
  'grip strengthener': { asin: 'B00F8I3IYK', name: 'Luxon Hand Grip Strengthener' },
  'hand grip': { asin: 'B00F8I3IYK', name: 'Luxon Hand Grip Strengthener' },
  'pull-up bands': { asin: 'B01AVDVHTI', name: 'Fit Simplify Resistance Loop Bands' },
  'cable machine': { asin: 'B07BM2KWDB', name: 'Fitness Reality Functional Trainer' },
  'speed bag': { asin: 'B01N4LRPN0', name: 'Everlast Speed Bag' },
  'boxing gloves': { asin: 'B01N4LRPN0', name: 'Everlast Pro Style Training Gloves' },
  'medicine ball': { asin: 'B071YYZPXJ', name: 'AmazonBasics Medicine Ball' },
  'bosu ball': { asin: 'B002YB3SZA', name: 'BOSU Balance Trainer' },
  'balance board': { asin: 'B07P5PR4SZ', name: 'Revolution Balance Board' },
  'gym equipment': { asin: 'B001ARYU58', name: 'Bowflex SelectTech 552 Adjustable Dumbbells' },
  'home gym': { asin: 'B001ARYU58', name: 'Bowflex SelectTech 552 Adjustable Dumbbells' },

  // Supplements
  'creatine': { asin: 'B002DYIZEO', name: 'Optimum Nutrition Micronized Creatine Monohydrate' },
  'creatine monohydrate': { asin: 'B002DYIZEO', name: 'Optimum Nutrition Micronized Creatine Monohydrate' },
  'protein powder': { asin: 'B000QSNYGI', name: 'Optimum Nutrition Gold Standard 100% Whey' },
  'whey protein': { asin: 'B000QSNYGI', name: 'Optimum Nutrition Gold Standard 100% Whey' },
  'protein': { asin: 'B000QSNYGI', name: 'Optimum Nutrition Gold Standard 100% Whey' },
  'pre workout': { asin: 'B072BTJLHK', name: 'Cellucor C4 Original Pre Workout' },
  'pre-workout': { asin: 'B072BTJLHK', name: 'Cellucor C4 Original Pre Workout' },
  'preworkout': { asin: 'B072BTJLHK', name: 'Cellucor C4 Original Pre Workout' },
  'bcaa': { asin: 'B00E95HP4O', name: 'Scivation Xtend BCAA Powder' },
  'fish oil': { asin: 'B004O2I9JO', name: 'Nordic Naturals Ultimate Omega' },
  'omega 3': { asin: 'B004O2I9JO', name: 'Nordic Naturals Ultimate Omega' },
  'omega-3': { asin: 'B004O2I9JO', name: 'Nordic Naturals Ultimate Omega' },
  'multivitamin': { asin: 'B00ARIRJ0G', name: 'Garden of Life Vitamin Code Men' },
  'vitamin d': { asin: 'B00GB85JR4', name: 'NatureWise Vitamin D3 5000IU' },
  'vitamin d3': { asin: 'B00GB85JR4', name: 'NatureWise Vitamin D3 5000IU' },
  'magnesium': { asin: 'B000BD0RT0', name: "Doctor's Best High Absorption Magnesium" },
  'magnesium glycinate': { asin: 'B000BD0RT0', name: "Doctor's Best High Absorption Magnesium Glycinate" },
  'zinc': { asin: 'B01KWUN2TM', name: 'Nature Made Zinc 30mg' },
  'ashwagandha': { asin: 'B078K18HYN', name: 'NaturaLife Labs Organic Ashwagandha' },
  'collagen': { asin: 'B00K6JUG40', name: 'Vital Proteins Collagen Peptides' },
  'collagen peptides': { asin: 'B00K6JUG40', name: 'Vital Proteins Collagen Peptides' },
  'electrolytes': { asin: 'B083FWBYNJ', name: 'LMNT Zero-Sugar Electrolytes' },
  'caffeine pills': { asin: 'B005HMHGGE', name: 'Nutricost Caffeine Pills 200mg' },
  'melatonin': { asin: 'B005DEK990', name: 'Natrol Melatonin Fast Dissolve' },
  'testosterone booster': { asin: 'B01DBJS40S', name: 'Nugenix Total-T Testosterone Booster' },
  'testosterone': { asin: 'B01DBJS40S', name: 'Nugenix Total-T Testosterone Booster' },
  'joint supplement': { asin: 'B07H4BHKWG', name: 'Move Free Advanced Glucosamine Chondroitin' },
  'glucosamine': { asin: 'B07H4BHKWG', name: 'Move Free Advanced Glucosamine Chondroitin' },
  'turmeric': { asin: 'B01DBTFO98', name: 'Qunol Turmeric Curcumin Softgels' },
  'curcumin': { asin: 'B01DBTFO98', name: 'Qunol Turmeric Curcumin Softgels' },
  'glutamine': { asin: 'B000GIQT2G', name: 'Optimum Nutrition Glutamine Powder' },
  'casein protein': { asin: 'B002DYIZEO', name: 'Optimum Nutrition Gold Standard Casein' },
  'plant protein': { asin: 'B07QD7TPGH', name: 'Garden of Life Sport Organic Plant-Based Protein' },
  'vegan protein': { asin: 'B07QD7TPGH', name: 'Garden of Life Sport Organic Plant-Based Protein' },
  'sleep supplement': { asin: 'B005DEK990', name: 'Natrol Melatonin Fast Dissolve' },
  'recovery supplement': { asin: 'B00E95HP4O', name: 'Scivation Xtend BCAA Powder' },
  'nitric oxide': { asin: 'B072BTJLHK', name: 'Cellucor C4 Original Pre Workout' },

  // Recovery & Accessories
  'foam roller kit': { asin: 'B0040EKZDY', name: 'LuxFit Premium High Density Foam Roller' },
  'lacrosse ball': { asin: 'B00BUSKM5O', name: 'Kieba Massage Lacrosse Balls' },
  'yoga blocks': { asin: 'B01LXBAQHQ', name: 'Gaiam Essentials Yoga Block Set' },
  'yoga block': { asin: 'B01LXBAQHQ', name: 'Gaiam Essentials Yoga Block Set' },
  'fitness tracker': { asin: 'B0B5F9SZW7', name: 'Fitbit Charge 5' },
  'smartwatch': { asin: 'B0B5F9SZW7', name: 'Fitbit Charge 5' },
  'heart rate monitor': { asin: 'B085NWD7MC', name: 'Polar H10 Heart Rate Monitor' },
  'gym bag': { asin: 'B08T1NMBYH', name: 'Under Armour Undeniable 5.0 Duffle Bag' },
  'shaker bottle': { asin: 'B01LZ2GH5O', name: 'BlenderBottle Classic V2' },
  'protein shaker': { asin: 'B01LZ2GH5O', name: 'BlenderBottle Classic V2' },
  'water bottle': { asin: 'B08FSGP6BQ', name: 'Hydro Flask Water Bottle' },
  'compression sleeves': { asin: 'B019PS4SBA', name: 'Nordic Lifting Knee Sleeves' },
  'compression socks': { asin: 'B00H4LMH4I', name: 'SB SOX Compression Socks' },
  'ice pack': { asin: 'B001ED9W6C', name: 'Reusable Ice Packs for Injuries' },
  'heating pad': { asin: 'B003BTCQVG', name: 'Sunbeam Heating Pad for Back Pain' },
  'tens unit': { asin: 'B005MI3OWC', name: 'TENS 7000 Digital TENS Unit' },

  // Nutrition & Meal Prep
  'meal prep containers': { asin: 'B078RFVKNR', name: 'Prep Naturals Glass Meal Prep Containers' },
  'meal prep': { asin: 'B078RFVKNR', name: 'Prep Naturals Glass Meal Prep Containers' },
  'food scale': { asin: 'B004164SRA', name: 'Ozeri Pronto Digital Kitchen Food Scale' },
  'kitchen scale': { asin: 'B004164SRA', name: 'Ozeri Pronto Digital Kitchen Food Scale' },
  'blender': { asin: 'B08PJ5DV37', name: 'Ninja BN701 Professional Plus Blender' },
  'air fryer': { asin: 'B07FDJMC9Q', name: 'COSORI Air Fryer Pro LE' },
  'instant pot': { asin: 'B00FLYWNYQ', name: 'Instant Pot Duo 7-in-1 Electric Pressure Cooker' },
  'food processor': { asin: 'B01AXM4WIY', name: 'Hamilton Beach Food Processor' },

  // Daily Deal Darling — Kitchen & Home
  'kitchen gadgets': { asin: 'B08PL9GGHQ', name: 'Kitchen Gadget Set' },
  'organizer': { asin: 'B07DFDS56B', name: 'SimpleHouseware Stackable Can Rack Organizer' },
  'storage bins': { asin: 'B073VB74FJ', name: 'Amazon Basics Collapsible Fabric Storage Cubes' },
  'storage bin': { asin: 'B073VB74FJ', name: 'Amazon Basics Collapsible Fabric Storage Cubes' },
  'cleaning supplies': { asin: 'B07NNHH4KG', name: 'MR.SIGA Microfiber Cleaning Cloth' },
  'microfiber cloths': { asin: 'B07NNHH4KG', name: 'MR.SIGA Microfiber Cleaning Cloth' },
  'vacuum': { asin: 'B07QXMNF1K', name: 'Shark Navigator Lift-Away Vacuum' },
  'robot vacuum': { asin: 'B0BVC7L9LH', name: 'iRobot Roomba Combo j5 Robot Vacuum' },
  'coffee maker': { asin: 'B07HGBD396', name: 'Keurig K-Classic Coffee Maker' },
  'cutting board': { asin: 'B005HEZJGC', name: 'John Boos Block Maple Wood Cutting Board' },
  'knife set': { asin: 'B07TLZXRK2', name: 'Home Hero Kitchen Knife Set' },
  'pots and pans': { asin: 'B01KWIDUG2', name: 'T-fal Platinum Nonstick Cookware Set' },
  'cookware': { asin: 'B01KWIDUG2', name: 'T-fal Platinum Nonstick Cookware Set' },
  'cast iron skillet': { asin: 'B00006JSUA', name: 'Lodge Pre-Seasoned Cast Iron Skillet' },
  'baking sheet': { asin: 'B0725GYTPN', name: 'Nordic Ware Natural Aluminum Commercial Baker Sheet' },
  'spice rack': { asin: 'B07D2C1KGH', name: 'SpaceAid Pull Out Spice Rack Organizer' },
  'ice maker': { asin: 'B07PP9TPRZ', name: 'Silonn Countertop Ice Maker Machine' },
  'dish rack': { asin: 'B07GKS2XH9', name: 'simplehuman Steel Frame Dish Rack' },

  // Beauty & Self-Care
  'skincare': { asin: 'B00TTD9BRC', name: 'CeraVe Daily Moisturizing Lotion' },
  'moisturizer': { asin: 'B00TTD9BRC', name: 'CeraVe Daily Moisturizing Lotion' },
  'face moisturizer': { asin: 'B00TTD9BRC', name: 'CeraVe Daily Moisturizing Lotion' },
  'face serum': { asin: 'B0060MYJTK', name: 'TruSkin Vitamin C Serum for Face' },
  'vitamin c serum': { asin: 'B0060MYJTK', name: 'TruSkin Vitamin C Serum for Face' },
  'retinol': { asin: 'B01ITTFGRS', name: 'RoC Retinol Correxion Deep Wrinkle Night Cream' },
  'retinol cream': { asin: 'B01ITTFGRS', name: 'RoC Retinol Correxion Deep Wrinkle Night Cream' },
  'sunscreen': { asin: 'B0060OUV3E', name: 'EltaMD UV Clear Broad-Spectrum SPF 46' },
  'spf': { asin: 'B0060OUV3E', name: 'EltaMD UV Clear Broad-Spectrum SPF 46' },
  'hair dryer': { asin: 'B084TGJ9VK', name: 'Dyson Supersonic Hair Dryer' },
  'flat iron': { asin: 'B073FHXF9D', name: 'BaBylissPRO Nano Titanium Flat Iron' },
  'hair straightener': { asin: 'B073FHXF9D', name: 'BaBylissPRO Nano Titanium Flat Iron' },
  'curling iron': { asin: 'B00RBEA2BC', name: 'BaBylissPRO Nano Titanium Curling Iron' },
  'curling wand': { asin: 'B00RBEA2BC', name: 'BaBylissPRO Nano Titanium Curling Iron' },
  'makeup brushes': { asin: 'B01LZ6RE86', name: 'BS-MALL Makeup Brushes Set' },
  'makeup brush set': { asin: 'B01LZ6RE86', name: 'BS-MALL Makeup Brushes Set' },
  'nail polish': { asin: 'B00TKLBS0A', name: 'Beetles Gel Nail Polish Kit' },
  'jade roller': { asin: 'B07F31WC8G', name: 'Baimei Jade Roller & Gua Sha Set' },
  'gua sha': { asin: 'B07F31WC8G', name: 'Baimei Jade Roller & Gua Sha Set' },
  'eye cream': { asin: 'B01FXC78AC', name: 'INNISFREE Retinol Cica Repair Eye Cream' },
  'lip balm': { asin: 'B004LLIKVU', name: "Burt's Bees Natural Moisturizing Lip Balm" },
  'body lotion': { asin: 'B0048EZECA', name: 'Jergens Ultra Healing Dry Skin Moisturizer' },
  'dry shampoo': { asin: 'B00B3XGP4W', name: 'Batiste Dry Shampoo' },
  'bath bombs': { asin: 'B01MFGN8FK', name: 'LifeAround2Angels Bath Bombs Gift Set' },
  'bath bomb': { asin: 'B01MFGN8FK', name: 'LifeAround2Angels Bath Bombs Gift Set' },
  'essential oils': { asin: 'B07572TT7Q', name: 'Lagunamoon Essential Oils Top 6 Gift Set' },
  'essential oil': { asin: 'B07572TT7Q', name: 'Lagunamoon Essential Oils Top 6 Gift Set' },
  'candles': { asin: 'B07P3SQCV3', name: 'Yankee Candle Large Jar Candle' },
  'candle': { asin: 'B07P3SQCV3', name: 'Yankee Candle Large Jar Candle' },
  'face mask': { asin: 'B00DGYB1KE', name: 'Aztec Secret Indian Healing Clay' },
  'clay mask': { asin: 'B00DGYB1KE', name: 'Aztec Secret Indian Healing Clay' },
  'toner': { asin: 'B082WG3T8Y', name: 'Thayers Witch Hazel Toner' },
  'witch hazel': { asin: 'B082WG3T8Y', name: 'Thayers Witch Hazel Toner' },
  'sheet mask': { asin: 'B07T3MPBTK', name: 'TONYMOLY I Am Real Sheet Mask Set' },
  'under eye patches': { asin: 'B07KC5DWCC', name: 'Peter Thomas Roth Eye Patches' },
  'under eye mask': { asin: 'B07KC5DWCC', name: 'Peter Thomas Roth Eye Patches' },
  'hair mask': { asin: 'B01LYNZLUY', name: 'Briogeo Dont Despair Repair Deep Conditioning Mask' },
  'hair treatment': { asin: 'B01LYNZLUY', name: 'Briogeo Dont Despair Repair Deep Conditioning Mask' },
  'nail care': { asin: 'B00TKLBS0A', name: 'Beetles Gel Nail Polish Kit' },
  'loofah': { asin: 'B07F5BSG7V', name: 'Shower Loofah Sponge Scrubber' },
  'bath brush': { asin: 'B07F5BSG7V', name: 'Shower Loofah Sponge Scrubber' },
  'electric toothbrush': { asin: 'B07HPFQP44', name: 'Oral-B Pro 1000 Electric Toothbrush' },
  'teeth whitening': { asin: 'B07VQMM3TS', name: 'Crest 3D Whitestrips' },
  'whitening strips': { asin: 'B07VQMM3TS', name: 'Crest 3D Whitestrips' },

  // Lifestyle & Wellness
  'planner': { asin: 'B0BW9GDRP7', name: 'Clever Fox Planner Pro' },
  'journal': { asin: 'B0BW9GDRP7', name: 'Clever Fox Planner Pro' },
  'sleep mask': { asin: 'B07KC5DWCC', name: 'MZOO Sleep Eye Mask' },
  'eye mask': { asin: 'B07KC5DWCC', name: 'MZOO Sleep Eye Mask' },
  'weighted blanket': { asin: 'B07H2DKQGJ', name: 'YnM Weighted Blanket' },
  'pillow': { asin: 'B07C7FQBDT', name: 'Coop Home Goods Adjustable Loft Pillow' },
  'cooling pillow': { asin: 'B07C7FQBDT', name: 'Coop Home Goods Eden Adjustable Pillow' },
  'desk organizer': { asin: 'B01CHKLYYK', name: 'SimpleHouseware Mesh Desk Organizer' },
  'standing desk': { asin: 'B089CZVSCJ', name: 'FEZIBO Standing Desk' },
  'blue light glasses': { asin: 'B0719RFLTQ', name: 'TIJN Blue Light Blocking Glasses' },
  'diffuser': { asin: 'B07L4R62GQ', name: 'InnoGear Essential Oil Diffuser' },
  'aromatherapy diffuser': { asin: 'B07L4R62GQ', name: 'InnoGear Essential Oil Diffuser' },

  // Menopause specific
  'hot flash relief': { asin: 'B001G7QUXW', name: 'Estroven Maximum Strength Menopause Relief' },
  'menopause supplements': { asin: 'B001G7QUXW', name: 'Estroven Maximum Strength Menopause Relief' },
  'menopause supplement': { asin: 'B001G7QUXW', name: 'Estroven Maximum Strength Menopause Relief' },
  'menopause relief': { asin: 'B001G7QUXW', name: 'Estroven Maximum Strength Menopause Relief' },
  'menopause tea': { asin: 'B000SATIFA', name: 'Traditional Medicinals Womens Healthy Cycle Tea' },
  'night sweats': { asin: 'B07YC684QN', name: 'Cool-jams Moisture Wicking Pajama Set' },
  'night sweats pajamas': { asin: 'B07YC684QN', name: 'Cool-jams Moisture Wicking Pajama Set' },
  'cooling pajamas': { asin: 'B07YC684QN', name: 'Cool-jams Moisture Wicking Pajama Set' },
  'sleep aid': { asin: 'B005DEK990', name: 'Natrol Melatonin Fast Dissolve Tablets' },
  'bone density': { asin: 'B001G7R5K6', name: 'Garden of Life Vitamin Code Raw Calcium' },
  'calcium supplement': { asin: 'B001G7R5K6', name: 'Garden of Life Vitamin Code Raw Calcium' },
  'black cohosh': { asin: 'B0019LTI86', name: 'Natures Way Black Cohosh Root' },
  'valerian': { asin: 'B0019LTI86', name: 'Natures Way Valerian Root' },
  'valerian root': { asin: 'B0019LTI86', name: 'Natures Way Valerian Root' },
  'cooling sheets': { asin: 'B07QDFLQ7J', name: 'Mellanni Cooling Bed Sheet Set' },
  'bamboo sheets': { asin: 'B07QDFLQ7J', name: 'Mellanni Cooling Bed Sheet Set' },
  'cooling mattress pad': { asin: 'B07JB1XNSP', name: 'Zen Bamboo Mattress Topper' },
  'mattress topper': { asin: 'B07JB1XNSP', name: 'Zen Bamboo Mattress Topper' },
  'hot flashes': { asin: 'B001G7QUXW', name: 'Estroven Maximum Strength Menopause Relief' },
  'perimenopause': { asin: 'B001G7QUXW', name: 'Estroven Maximum Strength Menopause Relief' },
  'hormone support': { asin: 'B001G7QUXW', name: 'Estroven Maximum Strength Menopause Relief' },
  'cooling sleepwear': { asin: 'B07YC684QN', name: 'Cool-jams Moisture Wicking Pajama Set' },
  'bamboo sleepwear': { asin: 'B07YC684QN', name: 'Cool-jams Moisture Wicking Pajama Set' },
  'vaginal dryness': { asin: 'B01B7W5K36', name: 'Replens Long-Lasting Vaginal Moisturizer' },
  'vaginal moisturizer': { asin: 'B01B7W5K36', name: 'Replens Long-Lasting Vaginal Moisturizer' },
  'mood support': { asin: 'B001G7QUXW', name: 'Estroven Maximum Strength + Mood & Memory' },
  'brain fog': { asin: 'B01DBJS40S', name: 'Neuriva Brain Performance Supplement' },
  'memory supplement': { asin: 'B01DBJS40S', name: 'Neuriva Brain Performance Supplement' },

  // Additional missing products
  'probiotic': { asin: 'B0C5VYZ9F8', name: 'Culturelle Daily Probiotic Capsules' },
  'probiotics': { asin: 'B0C5VYZ9F8', name: 'Culturelle Daily Probiotic Capsules' },
  'digestive enzymes': { asin: 'B005NWQY5M', name: 'NOW Foods Digestive Enzymes Complex' },
  'digestive enzyme': { asin: 'B005NWQY5M', name: 'NOW Foods Digestive Enzymes Complex' },
  'blackout curtains': { asin: 'B0CG8F8N3J', name: 'Thermal Insulated Blackout Curtain Panels' },
  'blackout curtain': { asin: 'B0CG8F8N3J', name: 'Thermal Insulated Blackout Curtain Panels' },
};

function normalizeQuery(query) {
  return query
    .toLowerCase()
    .replace(/\+/g, ' ')
    .replace(/%20/g, ' ')
    .replace(/%2B/g, ' ')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function findProduct(searchQuery) {
  const normalized = normalizeQuery(searchQuery);
  if (PRODUCT_MAP[normalized]) return PRODUCT_MAP[normalized];
  for (const [key, product] of Object.entries(PRODUCT_MAP)) {
    if (normalized.includes(key) || key.includes(normalized)) return product;
  }
  const queryWords = normalized.split(/\s+/).filter(w => w.length > 2);
  let bestMatch = null;
  let bestOverlap = 0;
  for (const [key, product] of Object.entries(PRODUCT_MAP)) {
    const keyWords = key.split(/\s+/);
    const overlap = queryWords.filter(w => keyWords.includes(w)).length;
    if (overlap > bestOverlap) { bestOverlap = overlap; bestMatch = product; }
  }
  if (bestOverlap > 0) return bestMatch;
  return null;
}

function extractSearchQuery(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.searchParams.get('k') || urlObj.searchParams.get('keywords') || '';
  } catch {
    const match = url.match(/[?&]k=([^&"'\s<>]+)/);
    return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : '';
  }
}

function buildAffiliateLink(asin) {
  return `https://www.amazon.com/dp/${asin}?tag=${AFFILIATE_TAG}`;
}

function processFile(filePath) {
  let content = readFileSync(filePath, 'utf-8');
  const original = content;
  let changes = [];

  // Fix search URLs
  const searchUrlRegex = /https?:\/\/(?:www\.)?amazon\.com\/s\?[^"'\s<>)]+/g;
  const searchMatches = [...new Set(content.match(searchUrlRegex) || [])];
  for (const oldUrl of searchMatches) {
    const query = extractSearchQuery(oldUrl);
    if (!query) continue;
    const product = findProduct(query);
    if (product) {
      content = content.split(oldUrl).join(buildAffiliateLink(product.asin));
      changes.push({ type: 'converted', old: oldUrl, product: product.name, asin: product.asin, query });
    } else {
      changes.push({ type: 'no_match', old: oldUrl, query });
    }
  }

  // Fix wrong tag
  const wrongTagCount = (content.match(/tag=fitover35-20/g) || []).length;
  if (wrongTagCount > 0) {
    content = content.replace(/tag=fitover35-20/g, `tag=${AFFILIATE_TAG}`);
    changes.push({ type: 'tag_fix', count: wrongTagCount });
  }

  // Add missing tag to /dp/ links
  const noTagRegex = /(https?:\/\/(?:www\.)?amazon\.com\/dp\/[A-Z0-9]{10})(?!\?tag=)(?=['">\s\)])/g;
  let noTagAdded = 0;
  content = content.replace(noTagRegex, (match, url) => { noTagAdded++; return `${url}?tag=${AFFILIATE_TAG}`; });
  if (noTagAdded > 0) changes.push({ type: 'tag_added', count: noTagAdded });

  if (content !== original) writeFileSync(filePath, content, 'utf-8');
  return changes;
}

function findHtmlFiles(dir) {
  let files = [];
  try {
    for (const entry of readdirSync(dir)) {
      const fullPath = join(dir, entry);
      const stat = statSync(fullPath);
      if (stat.isDirectory() && !['node_modules', '.git'].includes(entry)) {
        files = files.concat(findHtmlFiles(fullPath));
      } else if (entry.endsWith('.html')) {
        files.push(fullPath);
      }
    }
  } catch {}
  return files;
}

const HOME = process.env.HOME;
const SITE_DIRS = [
  `${HOME}/Desktop/social-media-empire/outputs/fitover35-website`,
  `${HOME}/Desktop/social-media-empire/outputs/dailydealdarling-website`,
];

let totalConverted = 0, totalTagFixed = 0, totalTagAdded = 0, totalFiles = 0;
const unmatched = [];

for (const dir of SITE_DIRS) {
  const files = findHtmlFiles(dir);
  if (!files.length) { console.log(`⚠️  No HTML files in: ${dir}`); continue; }
  console.log(`\n📁 ${dir.split('/').pop()} — ${files.length} files`);

  for (const file of files) {
    const changes = processFile(file);
    if (!changes.length) continue;
    totalFiles++;
    const fname = relative(dir, file);
    for (const c of changes) {
      if (c.type === 'converted') {
        totalConverted++;
        console.log(`  ✅ ${fname}: "${c.query}" → ${c.product} (${c.asin})`);
      } else if (c.type === 'no_match') {
        unmatched.push({ file: fname, query: c.query, url: c.old });
        console.log(`  ⚠️  ${fname}: NO MATCH for "${c.query}"`);
      } else if (c.type === 'tag_fix') {
        totalTagFixed += c.count;
        console.log(`  🏷️  ${fname}: fixed ${c.count} tag(s) fitover35-20 → ${AFFILIATE_TAG}`);
      } else if (c.type === 'tag_added') {
        totalTagAdded += c.count;
        console.log(`  🏷️  ${fname}: added tag to ${c.count} untagged link(s)`);
      }
    }
  }
}

console.log(`\n${'─'.repeat(50)}`);
console.log(`SUMMARY`);
console.log(`  Files modified  : ${totalFiles}`);
console.log(`  Search→Direct   : ${totalConverted}`);
console.log(`  Tags fixed      : ${totalTagFixed}`);
console.log(`  Tags added      : ${totalTagAdded}`);
console.log(`  Unmatched URLs  : ${unmatched.length}`);
if (unmatched.length) {
  console.log(`\nUNMATCHED (need manual lookup):`);
  for (const u of unmatched) console.log(`  [${u.file}] query="${u.query}"`);
}
