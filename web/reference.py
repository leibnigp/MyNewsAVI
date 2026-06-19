from flask import Blueprint, render_template

reference_bp = Blueprint("reference", __name__)

# FedEx known China routes (publicly documented)
FEDEX_CHINA_ROUTES = [
    {
        "origin": "Memphis (MEM)",
        "destination": "广州白云 (CAN)",
        "via": "安克雷奇 (ANC)",
        "frequency": "每周 7 班",
        "aircraft": "777F",
        "note": "FedEx 亚太枢纽，广州是 FedEx 美国以外最大的转运中心",
        "status": "运营中",
    },
    {
        "origin": "Memphis (MEM)",
        "destination": "上海浦东 (PVG)",
        "via": "安克雷奇 (ANC)",
        "frequency": "每周 7 班",
        "aircraft": "777F",
        "note": "华东核心门户航线",
        "status": "运营中",
    },
    {
        "origin": "Memphis (MEM)",
        "destination": "深圳宝安 (SZX)",
        "via": "安克雷奇 (ANC)",
        "frequency": "每周 5 班",
        "aircraft": "777F",
        "note": "覆盖华南电子制造/跨境电商密集区",
        "status": "运营中",
    },
    {
        "origin": "Memphis (MEM)",
        "destination": "北京首都 (PEK)",
        "via": "安克雷奇 (ANC) / 大阪关西 (KIX)",
        "frequency": "每周 5 班",
        "aircraft": "777F / 767-300F",
        "note": "华北门户，部分经停大阪",
        "status": "运营中",
    },
    {
        "origin": "广州白云 (CAN)",
        "destination": "大阪关西 (KIX)",
        "via": "",
        "frequency": "每周 3 班",
        "aircraft": "767-300F",
        "note": "亚太区域内 feeder 航线",
        "status": "运营中",
    },
    {
        "origin": "广州白云 (CAN)",
        "destination": "新加坡樟宜 (SIN)",
        "via": "",
        "frequency": "每周 3 班",
        "aircraft": "767-300F",
        "note": "东南亚转运连接",
        "status": "运营中",
    },
    {
        "origin": "上海浦东 (PVG)",
        "destination": "大阪关西 (KIX)",
        "via": "",
        "frequency": "每周 3 班",
        "aircraft": "767-300F",
        "note": "华东-日本快速连接",
        "status": "运营中",
    },
    {
        "origin": "广州白云 (CAN)",
        "destination": "安克雷奇 (ANC)",
        "via": "",
        "frequency": "每周 7 班",
        "aircraft": "777F",
        "note": "亚太-北美主通道，ANC 加油/换组后继续飞 MEM",
        "status": "运营中",
    },
    {
        "origin": "巴黎戴高乐 (CDG)",
        "destination": "广州白云 (CAN)",
        "via": "",
        "frequency": "每周 3 班",
        "aircraft": "777F",
        "note": "欧洲-中国直飞航线",
        "status": "运营中",
    },
    {
        "origin": "广州白云 (CAN)",
        "destination": "科隆波恩 (CGN)",
        "via": "",
        "frequency": "每周 2 班",
        "aircraft": "777F",
        "note": "FedEx 欧洲枢纽连接",
        "status": "运营中",
    },
]

UPS_CHINA_ROUTES = [
    {
        "origin": "路易斯维尔 (SDF)",
        "destination": "深圳宝安 (SZX)",
        "via": "安克雷奇 (ANC)",
        "frequency": "每周 7 班",
        "aircraft": "747-8F / MD-11F",
        "note": "UPS 亚洲新枢纽，替代原菲律宾克拉克转运中心",
        "status": "运营中",
    },
    {
        "origin": "路易斯维尔 (SDF)",
        "destination": "上海浦东 (PVG)",
        "via": "安克雷奇 (ANC)",
        "frequency": "每周 7 班",
        "aircraft": "747-8F / 747-400F",
        "note": "华东主干航线",
        "status": "运营中",
    },
    {
        "origin": "路易斯维尔 (SDF)",
        "destination": "北京首都 (PEK)",
        "via": "安克雷奇 (ANC)",
        "frequency": "每周 3-4 班",
        "aircraft": "747-8F / MD-11F",
        "note": "华北直达航线",
        "status": "运营中",
    },
    {
        "origin": "深圳宝安 (SZX)",
        "destination": "科隆波恩 (CGN)",
        "via": "",
        "frequency": "每周 5 班",
        "aircraft": "747-8F",
        "note": "欧洲主干线，深圳↔科隆直达",
        "status": "运营中",
    },
    {
        "origin": "深圳宝安 (SZX)",
        "destination": "新加坡樟宜 (SIN)",
        "via": "",
        "frequency": "每周 3 班",
        "aircraft": "767-300F",
        "note": "东南亚区域转运",
        "status": "运营中",
    },
    {
        "origin": "上海浦东 (PVG)",
        "destination": "大阪关西 (KIX)",
        "via": "",
        "frequency": "每周 3 班",
        "aircraft": "767-300F",
        "note": "日本区域连接",
        "status": "运营中",
    },
]

CHINA_AIRPORTS = [
    {"code": "CAN", "name": "广州白云国际机场", "city": "广州", "role": "FedEx 亚太枢纽"},
    {"code": "PVG", "name": "上海浦东国际机场", "city": "上海", "role": "FedEx/UPS 华东枢纽"},
    {"code": "SZX", "name": "深圳宝安国际机场", "city": "深圳", "role": "UPS 亚洲枢纽 / FedEx 华南枢纽"},
    {"code": "PEK", "name": "北京首都国际机场", "city": "北京", "role": "FedEx/UPS 华北门户"},
]

FEDEX_FLEET = [
    {"type": "777F", "payload": "102 吨", "range": "9,200 km", "count": "50+ 架"},
    {"type": "767-300F", "payload": "52 吨", "range": "6,000 km", "count": "120+ 架"},
    {"type": "757-200F", "payload": "36 吨", "range": "5,500 km", "count": "100+ 架"},
]

UPS_FLEET = [
    {"type": "747-8F", "payload": "134 吨", "range": "8,200 km", "count": "30+ 架"},
    {"type": "747-400F", "payload": "110 吨", "range": "8,200 km", "count": "10+ 架"},
    {"type": "MD-11F", "payload": "85 吨", "range": "7,300 km", "count": "40+ 架"},
    {"type": "767-300F", "payload": "52 吨", "range": "6,000 km", "count": "80+ 架"},
]


# FedEx Guangzhou CAN Hub detailed route network
CAN_HUB_ROUTES = {
    "trans_pacific": {
        "label": "跨太平洋主干线（北美方向）",
        "icon": "🌎",
        "routes": [
            {"dest": "安克雷奇 (ANC)", "dest_city": "美国阿拉斯加", "freq": "每周 7 班", "ac": "777F", "note": "北美方向必经经停点，加油换组后衔接 MEM/EWR/LAX 等"},
            {"dest": "孟菲斯 (MEM)", "dest_city": "美国田纳西", "freq": "每周 7 班（经 ANC）", "ac": "777F", "note": "FedEx 全球超级枢纽，CAN 发出的所有北美货邮经此分拨"},
            {"dest": "洛杉矶 (LAX)", "dest_city": "美国加利福尼亚", "freq": "每周 3 班（经 ANC）", "ac": "777F", "note": "美西分拨中心"},
            {"dest": "纽瓦克 (EWR)", "dest_city": "美国新泽西/纽约", "freq": "每周 3 班（经 ANC）", "ac": "777F", "note": "美东核心门户"},
            {"dest": "奥克兰 (OAK)", "dest_city": "美国加利福尼亚", "freq": "每周 3 班（经 ANC）", "ac": "777F / 767-300F", "note": "旧金山湾区覆盖"},
        ],
    },
    "europe": {
        "label": "欧洲方向",
        "icon": "🌍",
        "routes": [
            {"dest": "巴黎戴高乐 (CDG)", "dest_city": "法国", "freq": "每周 5 班", "ac": "777F", "note": "FedEx 欧洲最大枢纽，辐射西欧全境"},
            {"dest": "科隆波恩 (CGN)", "dest_city": "德国", "freq": "每周 3 班", "ac": "777F", "note": "德国/中欧分拨中心"},
            {"dest": "列日 (LGG)", "dest_city": "比利时", "freq": "每周 2 班", "ac": "777F", "note": "比荷卢地区门户"},
        ],
    },
    "northeast_asia": {
        "label": "东北亚区域网络",
        "icon": "🗾",
        "routes": [
            {"dest": "东京成田 (NRT)", "dest_city": "日本", "freq": "每周 5 班", "ac": "767-300F", "note": "日本核心枢纽，接驳 FedEx 日本国内网络"},
            {"dest": "大阪关西 (KIX)", "dest_city": "日本", "freq": "每周 5 班", "ac": "767-300F", "note": "关西经济圈覆盖"},
            {"dest": "首尔仁川 (ICN)", "dest_city": "韩国", "freq": "每周 5 班", "ac": "767-300F", "note": "韩国转运枢纽"},
            {"dest": "台北桃园 (TPE)", "dest_city": "中国台湾", "freq": "每周 3 班", "ac": "757-200F / 767-300F", "note": "台湾市场连接，电子零部件为主"},
        ],
    },
    "southeast_asia": {
        "label": "东南亚区域网络",
        "icon": "🏝",
        "routes": [
            {"dest": "新加坡樟宜 (SIN)", "dest_city": "新加坡", "freq": "每周 5 班", "ac": "767-300F", "note": "东南亚核心转运枢纽"},
            {"dest": "曼谷素万那普 (BKK)", "dest_city": "泰国", "freq": "每周 3 班", "ac": "767-300F", "note": "泰国/印支半岛覆盖"},
            {"dest": "胡志明市新山一 (SGN)", "dest_city": "越南", "freq": "每周 5 班", "ac": "767-300F", "note": "越南制造/电子出口大线"},
            {"dest": "河内内排 (HAN)", "dest_city": "越南", "freq": "每周 3 班", "ac": "767-300F", "note": "越南北部工业区覆盖"},
            {"dest": "槟城 (PEN)", "dest_city": "马来西亚", "freq": "每周 3 班", "ac": "767-300F / 757-200F", "note": "马来西亚电子产业带"},
            {"dest": "吉隆坡 (KUL)", "dest_city": "马来西亚", "freq": "每周 3 班", "ac": "767-300F", "note": "马来西亚首都覆盖"},
            {"dest": "马尼拉 (MNL)", "dest_city": "菲律宾", "freq": "每周 3 班", "ac": "767-300F", "note": "菲律宾市场"},
            {"dest": "雅加达 (CGK)", "dest_city": "印度尼西亚", "freq": "每周 3 班", "ac": "767-300F", "note": "印尼市场"},
        ],
    },
    "south_asia_me": {
        "label": "南亚 & 中东方向",
        "icon": "🌏",
        "routes": [
            {"dest": "德里 (DEL)", "dest_city": "印度", "freq": "每周 5 班", "ac": "767-300F", "note": "印度核心门户"},
            {"dest": "孟买 (BOM)", "dest_city": "印度", "freq": "每周 3 班", "ac": "767-300F", "note": "印度西部经济中心"},
            {"dest": "迪拜 (DXB)", "dest_city": "阿联酋", "freq": "每周 5 班", "ac": "777F / 767-300F", "note": "中东/非洲中转枢纽，接驳 FedEx 中东网络"},
        ],
    },
    "oceania": {
        "label": "大洋洲方向",
        "icon": "🦘",
        "routes": [
            {"dest": "悉尼 (SYD)", "dest_city": "澳大利亚", "freq": "每周 3 班", "ac": "767-300F", "note": "澳洲主要门户"},
            {"dest": "墨尔本 (MEL)", "dest_city": "澳大利亚", "freq": "每周 2 班", "ac": "767-300F", "note": "澳洲南部门户"},
        ],
    },
    "domestic": {
        "label": "国内城市 feeder 航线",
        "icon": "🇨🇳",
        "routes": [
            {"dest": "上海浦东 (PVG)", "dest_city": "上海", "freq": "每周 7 班", "ac": "767-300F / 757-200F", "note": "华东货邮经 CAN 中转至全球"},
            {"dest": "北京首都 (PEK)", "dest_city": "北京", "freq": "每周 5 班", "ac": "767-300F / 757-200F", "note": "华北集货 feeder"},
            {"dest": "深圳宝安 (SZX)", "dest_city": "深圳", "freq": "每周 5 班", "ac": "757-200F", "note": "珠三角区域内短途 feeder"},
        ],
    },
}

CAN_HUB_SUMMARY = {
    "hub_name": "FedEx 广州白云亚太转运中心",
    "location": "广州白云国际机场 (CAN)，货运区占地约 63,000 ㎡",
    "opened": "2009年2月正式启用（原苏比克湾枢纽迁至广州）",
    "role": "美国以外全球最大 FedEx 转运中心，亚太区域超级枢纽",
    "weekly_flights": "约 110+ 班/周（包括进港+出港）",
    "connected_continents": "北美、欧洲、亚洲（东亚/东南亚/南亚）、中东、大洋洲",
    "main_aircraft": "777F（跨洲洲际）+ 767-300F（亚太区域内）+ 757-200F（短途/feeder）",
    "sort_capacity": "每小时约 24,000 件包裹和文件分拣能力",
    "key_commodities": "电子产品、跨境电商包裹、汽车零部件、医药、半导体、时尚奢侈品",
}


# ====== UPS 深圳 SZX 枢纽 ======
UPS_SZX_SUMMARY = {
    "hub_name": "UPS 深圳宝安亚太转运中心",
    "location": "深圳宝安国际机场 (SZX)，专用货运设施",
    "opened": "2024年从菲律宾克拉克 (CRK) 迁至深圳",
    "role": "UPS 亚洲核心转运枢纽，替代原克拉克枢纽",
    "weekly_flights": "约 45+ 班/周",
    "connected_continents": "北美、欧洲、亚洲",
    "main_aircraft": "747-8F（洲际）+ 767-300F / MD-11F（区域）",
    "sort_capacity": "与深圳机场合作专用货站",
    "key_commodities": "电子产品、跨境电商、汽车零部件、医疗器械、半导体",
}

UPS_SZX_ROUTES = {
    "north_america": {
        "label": "北美方向",
        "routes": [
            {"dest": "路易斯维尔 (SDF)", "dest_city": "美国肯塔基", "freq": "每周 7 班（经 ANC）", "ac": "747-8F", "note": "UPS 全球超级枢纽 Worldport"},
            {"dest": "安克雷奇 (ANC)", "dest_city": "美国阿拉斯加", "freq": "每周 7 班", "ac": "747-8F / MD-11F", "note": "跨太平洋经停加油/换组"},
            {"dest": "安大略 (ONT)", "dest_city": "美国加利福尼亚", "freq": "每周 3 班（经 ANC）", "ac": "747-8F / MD-11F", "note": "美西区域枢纽"},
            {"dest": "费城 (PHL)", "dest_city": "美国宾夕法尼亚", "freq": "每周 3 班（经 ANC）", "ac": "747-8F", "note": "美东辅助门户"},
        ],
    },
    "europe": {
        "label": "欧洲方向",
        "routes": [
            {"dest": "科隆波恩 (CGN)", "dest_city": "德国", "freq": "每周 5 班", "ac": "747-8F", "note": "UPS 欧洲枢纽，深圳直达"},
            {"dest": "伊斯坦布尔 (IST)", "dest_city": "土耳其", "freq": "每周 2 班", "ac": "767-300F", "note": "欧亚中转点"},
        ],
    },
    "asia_pacific": {
        "label": "亚太区域内",
        "routes": [
            {"dest": "新加坡樟宜 (SIN)", "dest_city": "新加坡", "freq": "每周 5 班", "ac": "767-300F", "note": "东南亚分拨中心"},
            {"dest": "东京成田 (NRT)", "dest_city": "日本", "freq": "每周 5 班", "ac": "767-300F", "note": "日本枢纽"},
            {"dest": "大阪关西 (KIX)", "dest_city": "日本", "freq": "每周 3 班", "ac": "767-300F", "note": "关西覆盖"},
            {"dest": "首尔仁川 (ICN)", "dest_city": "韩国", "freq": "每周 5 班", "ac": "767-300F", "note": "韩国转运中心"},
            {"dest": "台北桃园 (TPE)", "dest_city": "中国台湾", "freq": "每周 3 班", "ac": "757-200F", "note": "台湾连接"},
        ],
    },
    "domestic": {
        "label": "国内 Feeder",
        "routes": [
            {"dest": "上海浦东 (PVG)", "dest_city": "上海", "freq": "每周 5 班", "ac": "757-200F / 767-300F", "note": "华东货邮经 SZX 中转"},
            {"dest": "郑州新郑 (CGO)", "dest_city": "郑州", "freq": "每周 5 班", "ac": "757-200F", "note": "中部枢纽 feeder"},
            {"dest": "北京首都 (PEK)", "dest_city": "北京", "freq": "每周 3 班", "ac": "757-200F", "note": "华北集货"},
        ],
    },
}

# ====== UPS 上海浦东 PVG 枢纽 ======
UPS_PVG_SUMMARY = {
    "hub_name": "UPS 上海浦东国际转运中心",
    "location": "上海浦东国际机场 (PVG)",
    "opened": "2008年正式启用",
    "role": "UPS 中国华东门户，连接 UPS 全球网络的重要节点",
    "weekly_flights": "约 35+ 班/周",
    "connected_continents": "北美、欧洲、亚洲",
    "main_aircraft": "747-8F / 747-400F（洲际）+ 767-300F / MD-11F（区域）",
    "sort_capacity": "上海国际转运中心，处理华东进出口货邮",
    "key_commodities": "电子产品、汽车零部件、高端制造、医药、跨境电商",
}

UPS_PVG_ROUTES = {
    "north_america": {
        "label": "北美方向",
        "routes": [
            {"dest": "路易斯维尔 (SDF)", "dest_city": "美国肯塔基", "freq": "每周 7 班（经 ANC）", "ac": "747-8F / 747-400F", "note": "UPS Worldport 主连接"},
            {"dest": "安克雷奇 (ANC)", "dest_city": "美国阿拉斯加", "freq": "每周 7 班", "ac": "747-8F / MD-11F", "note": "跨太平洋经停点"},
        ],
    },
    "europe": {
        "label": "欧洲方向",
        "routes": [
            {"dest": "科隆波恩 (CGN)", "dest_city": "德国", "freq": "每周 5 班", "ac": "747-8F", "note": "PVG↔CGN 欧洲主干线"},
        ],
    },
    "asia_pacific": {
        "label": "亚太区域内",
        "routes": [
            {"dest": "东京成田 (NRT)", "dest_city": "日本", "freq": "每周 5 班", "ac": "767-300F", "note": "日本枢纽"},
            {"dest": "大阪关西 (KIX)", "dest_city": "日本", "freq": "每周 5 班", "ac": "767-300F / MD-11F", "note": "关西大线，电子/汽车零部件"},
            {"dest": "首尔仁川 (ICN)", "dest_city": "韩国", "freq": "每周 5 班", "ac": "767-300F", "note": "韩国转运中心"},
        ],
    },
    "domestic": {
        "label": "国内 Feeder",
        "routes": [
            {"dest": "深圳宝安 (SZX)", "dest_city": "深圳", "freq": "每周 5 班", "ac": "757-200F / 767-300F", "note": "华南 feeder 至深圳枢纽"},
            {"dest": "郑州新郑 (CGO)", "dest_city": "郑州", "freq": "每周 3 班", "ac": "757-200F", "note": "中部连接"},
        ],
    },
}

# ====== UPS 郑州 CGO 枢纽 ======
UPS_CGO_SUMMARY = {
    "hub_name": "UPS 郑州航空货运枢纽",
    "location": "郑州新郑国际机场 (CGO)",
    "opened": "2012年逐步建立，近年持续扩大",
    "role": "UPS 中国中部核心门户，跨境电商/电子产品集散地",
    "weekly_flights": "约 20+ 班/周",
    "connected_continents": "北美、欧洲、亚洲",
    "main_aircraft": "747-8F / MD-11F（洲际）+ 767-300F / 757-200F（区域）",
    "sort_capacity": "郑州机场货运区 UPS 专用设施",
    "key_commodities": "电子产品（富士康/iPhone产业链）、跨境电商、汽车零部件",
}

UPS_CGO_ROUTES = {
    "north_america": {
        "label": "北美方向",
        "routes": [
            {"dest": "路易斯维尔 (SDF)", "dest_city": "美国肯塔基", "freq": "每周 5 班（经 ANC）", "ac": "747-8F / MD-11F", "note": "中部直达北美主干线"},
            {"dest": "安克雷奇 (ANC)", "dest_city": "美国阿拉斯加", "freq": "每周 5 班", "ac": "747-8F / MD-11F", "note": "跨太平洋经停加油"},
        ],
    },
    "europe": {
        "label": "欧洲方向",
        "routes": [
            {"dest": "科隆波恩 (CGN)", "dest_city": "德国", "freq": "每周 3 班", "ac": "747-8F / MD-11F", "note": "CGO↔CGN 中部-欧洲直达"},
        ],
    },
    "asia_pacific": {
        "label": "亚太区域内",
        "routes": [
            {"dest": "首尔仁川 (ICN)", "dest_city": "韩国", "freq": "每周 5 班", "ac": "767-300F", "note": "韩国电子产业链紧密连接"},
            {"dest": "东京成田 (NRT)", "dest_city": "日本", "freq": "每周 3 班", "ac": "767-300F", "note": "日本连接"},
        ],
    },
}

# ====== FedEx 上海浦东 PVG 枢纽 ======
FEDEX_PVG_SUMMARY = {
    "hub_name": "FedEx 上海浦东国际口岸/转运中心",
    "location": "上海浦东国际机场 (PVG)，FedEx 中国总部所在地",
    "opened": "2005年升级为国际口岸，持续扩建",
    "role": "FedEx 中国第二大枢纽（仅次于 CAN），华东核心门户",
    "weekly_flights": "约 55+ 班/周",
    "connected_continents": "北美、欧洲、亚洲",
    "main_aircraft": "777F（洲际）+ 767-300F / 757-200F（区域）",
    "sort_capacity": "浦东 FedEx 自有货站，处理华东进出口",
    "key_commodities": "电子产品、汽车零部件、半导体设备、时尚奢侈品、医药",
}

FEDEX_PVG_ROUTES = {
    "trans_pacific": {
        "label": "跨太平洋（北美方向）",
        "routes": [
            {"dest": "孟菲斯 (MEM)", "dest_city": "美国田纳西", "freq": "每周 7 班（经 ANC）", "ac": "777F", "note": "PVG 直达 FedEx 全球超级枢纽"},
            {"dest": "安克雷奇 (ANC)", "dest_city": "美国阿拉斯加", "freq": "每周 7 班", "ac": "777F", "note": "跨太平洋必经经停"},
            {"dest": "洛杉矶 (LAX)", "dest_city": "美国加利福尼亚", "freq": "每周 3 班（经 ANC）", "ac": "777F", "note": "美西分拨"},
            {"dest": "奥克兰 (OAK)", "dest_city": "美国加利福尼亚", "freq": "每周 3 班（经 ANC）", "ac": "777F", "note": "旧金山湾区"},
        ],
    },
    "europe": {
        "label": "欧洲方向",
        "routes": [
            {"dest": "巴黎戴高乐 (CDG)", "dest_city": "法国", "freq": "每周 3 班", "ac": "777F", "note": "FedEx 欧洲主枢纽"},
            {"dest": "科隆波恩 (CGN)", "dest_city": "德国", "freq": "每周 2 班", "ac": "777F", "note": "德国/中欧"},
        ],
    },
    "asia_pacific": {
        "label": "亚太区域内",
        "routes": [
            {"dest": "东京成田 (NRT)", "dest_city": "日本", "freq": "每周 5 班", "ac": "767-300F", "note": "日本核心连接"},
            {"dest": "大阪关西 (KIX)", "dest_city": "日本", "freq": "每周 5 班", "ac": "767-300F", "note": "关西直达"},
            {"dest": "首尔仁川 (ICN)", "dest_city": "韩国", "freq": "每周 3 班", "ac": "767-300F", "note": "韩国连接"},
        ],
    },
    "domestic": {
        "label": "国内 Feeder",
        "routes": [
            {"dest": "广州白云 (CAN)", "dest_city": "广州", "freq": "每周 7 班", "ac": "767-300F / 757-200F", "note": "华东↔华南枢纽双向 feeder"},
            {"dest": "北京首都 (PEK)", "dest_city": "北京", "freq": "每周 5 班", "ac": "757-200F", "note": "华北 feeder"},
            {"dest": "深圳宝安 (SZX)", "dest_city": "深圳", "freq": "每周 5 班", "ac": "757-200F", "note": "华南连接"},
            {"dest": "厦门高崎 (XMN)", "dest_city": "厦门", "freq": "每周 3 班", "ac": "757-200F", "note": "福建/东南 feeder"},
        ],
    },
}

# ====== FedEx 北京首都 PEK 枢纽 ======
FEDEX_PEK_SUMMARY = {
    "hub_name": "FedEx 北京首都国际口岸",
    "location": "北京首都国际机场 (PEK)",
    "opened": "2000年代至今持续运营",
    "role": "FedEx 华北门户，京津经济圈进出口核心节点",
    "weekly_flights": "约 25+ 班/周",
    "connected_continents": "北美、亚洲",
    "main_aircraft": "777F（洲际）+ 767-300F / 757-200F（区域）",
    "sort_capacity": "首都机场 FedEx 专用货站",
    "key_commodities": "电子产品、医药/疫苗冷链、汽车零部件、高端制造",
}

FEDEX_PEK_ROUTES = {
    "trans_pacific": {
        "label": "跨太平洋（北美方向）",
        "routes": [
            {"dest": "孟菲斯 (MEM)", "dest_city": "美国田纳西", "freq": "每周 5 班（经 ANC/KIX）", "ac": "777F / 767-300F", "note": "PEK 直达全球枢纽，部分经停大阪"},
            {"dest": "安克雷奇 (ANC)", "dest_city": "美国阿拉斯加", "freq": "每周 5 班", "ac": "777F", "note": "跨太平洋经停"},
            {"dest": "大阪关西 (KIX)", "dest_city": "日本", "freq": "每周 5 班", "ac": "767-300F", "note": "部分航班经 KIX 后继续飞 MEM"},
        ],
    },
    "asia_pacific": {
        "label": "亚太区域内",
        "routes": [
            {"dest": "东京成田 (NRT)", "dest_city": "日本", "freq": "每周 3 班", "ac": "767-300F", "note": "日本连接"},
            {"dest": "首尔仁川 (ICN)", "dest_city": "韩国", "freq": "每周 3 班", "ac": "767-300F", "note": "韩国连接"},
        ],
    },
    "domestic": {
        "label": "国内 Feeder",
        "routes": [
            {"dest": "广州白云 (CAN)", "dest_city": "广州", "freq": "每周 5 班", "ac": "767-300F / 757-200F", "note": "华北↔华南枢纽"},
            {"dest": "上海浦东 (PVG)", "dest_city": "上海", "freq": "每周 5 班", "ac": "757-200F", "note": "华北↔华东"},
            {"dest": "深圳宝安 (SZX)", "dest_city": "深圳", "freq": "每周 3 班", "ac": "757-200F", "note": "华南连接"},
        ],
    },
}

# ====== FedEx 深圳宝安 SZX 枢纽 ======
FEDEX_SZX_SUMMARY = {
    "hub_name": "FedEx 深圳宝安口岸",
    "location": "深圳宝安国际机场 (SZX)",
    "opened": "2010年代逐步扩大运营",
    "role": "FedEx 华南重要口岸，珠三角电子/跨境电商核心节点",
    "weekly_flights": "约 25+ 班/周",
    "connected_continents": "北美、亚洲",
    "main_aircraft": "777F（洲际）+ 767-300F / 757-200F（区域）",
    "sort_capacity": "深圳机场 FedEx 专用货站",
    "key_commodities": "电子产品（华为/大疆/供应链）、跨境电商（SHEIN/Temu）、半导体",
}

FEDEX_SZX_ROUTES = {
    "trans_pacific": {
        "label": "跨太平洋（北美方向）",
        "routes": [
            {"dest": "孟菲斯 (MEM)", "dest_city": "美国田纳西", "freq": "每周 5 班（经 ANC）", "ac": "777F", "note": "SZX 直达 MEM 全球枢纽"},
            {"dest": "安克雷奇 (ANC)", "dest_city": "美国阿拉斯加", "freq": "每周 5 班", "ac": "777F", "note": "跨太平洋经停"},
        ],
    },
    "asia_pacific": {
        "label": "亚太区域内",
        "routes": [
            {"dest": "东京成田 (NRT)", "dest_city": "日本", "freq": "每周 3 班", "ac": "767-300F", "note": "日本连接"},
            {"dest": "新加坡樟宜 (SIN)", "dest_city": "新加坡", "freq": "每周 3 班", "ac": "767-300F", "note": "东南亚转运"},
            {"dest": "台北桃园 (TPE)", "dest_city": "中国台湾", "freq": "每周 3 班", "ac": "757-200F", "note": "台湾电子产业链"},
        ],
    },
    "domestic": {
        "label": "国内 Feeder",
        "routes": [
            {"dest": "广州白云 (CAN)", "dest_city": "广州", "freq": "每周 5 班", "ac": "757-200F", "note": "珠三角区域内至 CAN 枢纽"},
            {"dest": "上海浦东 (PVG)", "dest_city": "上海", "freq": "每周 5 班", "ac": "757-200F", "note": "华南↔华东"},
            {"dest": "北京首都 (PEK)", "dest_city": "北京", "freq": "每周 3 班", "ac": "757-200F", "note": "华南↔华北"},
            {"dest": "厦门高崎 (XMN)", "dest_city": "厦门", "freq": "每周 3 班", "ac": "757-200F", "note": "福建 feeder"},
        ],
    },
}

# ====== FedEx 厦门高崎 XMN 枢纽 ======
FEDEX_XMN_SUMMARY = {
    "hub_name": "FedEx 厦门高崎口岸",
    "location": "厦门高崎国际机场 (XMN)",
    "opened": "2010年代逐步发展",
    "role": "FedEx 福建/东南沿海重要口岸，服务闽南经济圈及台湾海峡两岸货运",
    "weekly_flights": "约 15+ 班/周",
    "connected_continents": "亚洲（主要通过 CAN/PVG 中转全球）",
    "main_aircraft": "757-200F / 767-300F",
    "sort_capacity": "厦门机场 FedEx 货站",
    "key_commodities": "电子产品、鞋服纺织、石材、茶叶/食品、跨境电商",
}

FEDEX_XMN_ROUTES = {
    "asia_pacific": {
        "label": "亚太方向",
        "routes": [
            {"dest": "台北桃园 (TPE)", "dest_city": "中国台湾", "freq": "每周 3 班", "ac": "757-200F", "note": "两岸货运快速通道，电子/半导体"},
            {"dest": "东京成田 (NRT)", "dest_city": "日本", "freq": "每周 3 班", "ac": "767-300F", "note": "日本连接"},
            {"dest": "大阪关西 (KIX)", "dest_city": "日本", "freq": "每周 2 班", "ac": "757-200F", "note": "关西区域"},
            {"dest": "首尔仁川 (ICN)", "dest_city": "韩国", "freq": "每周 2 班", "ac": "767-300F", "note": "韩国连接"},
        ],
    },
    "domestic": {
        "label": "国内 Feeder（至主要枢纽中转全球）",
        "routes": [
            {"dest": "广州白云 (CAN)", "dest_city": "广州", "freq": "每周 5 班", "ac": "757-200F", "note": "至 CAN 枢纽中转全球网络"},
            {"dest": "上海浦东 (PVG)", "dest_city": "上海", "freq": "每周 3 班", "ac": "757-200F", "note": "至 PVG 口中转北美/欧洲"},
            {"dest": "深圳宝安 (SZX)", "dest_city": "深圳", "freq": "每周 3 班", "ac": "757-200F", "note": "区域短途 feeder"},
        ],
    },
}

# ====== All secondary hubs for template ======
SECONDARY_HUBS = [
    {
        "key": "ups_szx",
        "title": "UPS 深圳宝安 (SZX) 亚太转运中心",
        "color": "amber",
        "summary": UPS_SZX_SUMMARY,
        "routes": UPS_SZX_ROUTES,
    },
    {
        "key": "ups_pvg",
        "title": "UPS 上海浦东 (PVG) 国际转运中心",
        "color": "amber",
        "summary": UPS_PVG_SUMMARY,
        "routes": UPS_PVG_ROUTES,
    },
    {
        "key": "ups_cgo",
        "title": "UPS 郑州新郑 (CGO) 航空货运枢纽",
        "color": "amber",
        "summary": UPS_CGO_SUMMARY,
        "routes": UPS_CGO_ROUTES,
    },
    {
        "key": "fedex_pvg",
        "title": "FedEx 上海浦东 (PVG) 国际口岸",
        "color": "blue",
        "summary": FEDEX_PVG_SUMMARY,
        "routes": FEDEX_PVG_ROUTES,
    },
    {
        "key": "fedex_pek",
        "title": "FedEx 北京首都 (PEK) 国际口岸",
        "color": "blue",
        "summary": FEDEX_PEK_SUMMARY,
        "routes": FEDEX_PEK_ROUTES,
    },
    {
        "key": "fedex_szx",
        "title": "FedEx 深圳宝安 (SZX) 口岸",
        "color": "blue",
        "summary": FEDEX_SZX_SUMMARY,
        "routes": FEDEX_SZX_ROUTES,
    },
    {
        "key": "fedex_xmn",
        "title": "FedEx 厦门高崎 (XMN) 口岸",
        "color": "blue",
        "summary": FEDEX_XMN_SUMMARY,
        "routes": FEDEX_XMN_ROUTES,
    },
]


@reference_bp.route("/reference")
def reference():
    return render_template(
        "reference.html",
        fedex_routes=FEDEX_CHINA_ROUTES,
        ups_routes=UPS_CHINA_ROUTES,
        airports=CHINA_AIRPORTS,
        fedex_fleet=FEDEX_FLEET,
        ups_fleet=UPS_FLEET,
        can_hub_routes=CAN_HUB_ROUTES,
        can_hub_summary=CAN_HUB_SUMMARY,
        secondary_hubs=SECONDARY_HUBS,
    )
