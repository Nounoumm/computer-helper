"""初始化数据库并填充示例数据"""
import asyncio
import json
from sqlalchemy import select
from app.database import engine, AsyncSessionLocal, init_db
from app.models import Base, Component, Price


SEED_COMPONENTS = [
    # CPU
    {"name": "Intel Core i5-13400F", "component_type": "cpu", "brand": "Intel", "model": "i5-13400F",
     "performance_score": 75, "aesthetics_score": 50, "power_consumption": 65, "socket": "LGA1700", "prices": [1200]},
    {"name": "Intel Core i7-13700K", "component_type": "cpu", "brand": "Intel", "model": "i7-13700K",
     "performance_score": 92, "aesthetics_score": 55, "power_consumption": 125, "socket": "LGA1700", "prices": [2599]},
    {"name": "AMD Ryzen 5 5600", "component_type": "cpu", "brand": "AMD", "model": "R5 5600",
     "performance_score": 72, "aesthetics_score": 50, "power_consumption": 65, "socket": "AM4", "prices": [899]},
    {"name": "AMD Ryzen 7 7800X3D", "component_type": "cpu", "brand": "AMD", "model": "R7 7800X3D",
     "performance_score": 95, "aesthetics_score": 60, "power_consumption": 120, "socket": "AM5", "prices": [2499]},
    {"name": "Intel Core i3-12100F", "component_type": "cpu", "brand": "Intel", "model": "i3-12100F",
     "performance_score": 58, "aesthetics_score": 45, "power_consumption": 58, "socket": "LGA1700", "prices": [599]},
    # GPU
    {"name": "NVIDIA RTX 4060", "component_type": "gpu", "brand": "NVIDIA", "model": "RTX 4060",
     "performance_score": 78, "aesthetics_score": 65, "power_consumption": 115, "prices": [2399]},
    {"name": "NVIDIA RTX 4070", "component_type": "gpu", "brand": "NVIDIA", "model": "RTX 4070",
     "performance_score": 88, "aesthetics_score": 70, "power_consumption": 200, "prices": [4299]},
    {"name": "NVIDIA RTX 3060", "component_type": "gpu", "brand": "NVIDIA", "model": "RTX 3060",
     "performance_score": 68, "aesthetics_score": 60, "power_consumption": 170, "prices": [1999]},
    {"name": "AMD RX 7600", "component_type": "gpu", "brand": "AMD", "model": "RX 7600",
     "performance_score": 72, "aesthetics_score": 62, "power_consumption": 165, "prices": [1899]},
    {"name": "Intel Arc A750", "component_type": "gpu", "brand": "Intel", "model": "Arc A750",
     "performance_score": 70, "aesthetics_score": 68, "power_consumption": 225, "prices": [1699]},
    # 主板
    {"name": "华硕 B760M-PLUS", "component_type": "motherboard", "brand": "ASUS", "model": "B760M-PLUS",
     "performance_score": 70, "aesthetics_score": 75, "chipset": "B760", "form_factor": "mATX", "prices": [899]},
    {"name": "微星 B650M MORTAR", "component_type": "motherboard", "brand": "MSI", "model": "B650M",
     "performance_score": 72, "aesthetics_score": 78, "chipset": "B650", "form_factor": "mATX", "prices": [1099]},
    {"name": "华擎 B660M", "component_type": "motherboard", "brand": "ASRock", "model": "B660M",
     "performance_score": 65, "aesthetics_score": 55, "chipset": "B660", "form_factor": "mATX", "prices": [599]},
    # 内存
    {"name": "金士顿 16GB DDR5 5200", "component_type": "ram", "brand": "Kingston", "model": "DDR5 5200 16G",
     "performance_score": 72, "aesthetics_score": 50, "power_consumption": 5, "prices": [399]},
    {"name": "威刚 32GB DDR5 6000", "component_type": "ram", "brand": "ADATA", "model": "DDR5 6000 32G",
     "performance_score": 85, "aesthetics_score": 70, "rgb_support": True, "prices": [699]},
    {"name": "芝奇 16GB DDR4 3200", "component_type": "ram", "brand": "G.Skill", "model": "DDR4 3200 16G",
     "performance_score": 60, "aesthetics_score": 75, "rgb_support": True, "prices": [299]},
    # 存储
    {"name": "三星 980 1TB NVMe", "component_type": "storage", "brand": "Samsung", "model": "980 1TB",
     "performance_score": 80, "aesthetics_score": 50, "prices": [499]},
    {"name": "西数 SN770 1TB", "component_type": "storage", "brand": "WD", "model": "SN770 1TB",
     "performance_score": 78, "aesthetics_score": 55, "prices": [429]},
    {"name": "致钛 TiPlus5000 512GB", "component_type": "storage", "brand": "ZhiTai", "model": "TiPlus5000 512G",
     "performance_score": 70, "aesthetics_score": 50, "prices": [249]},
    # 电源
    {"name": "海韵 FOCUS 650W", "component_type": "psu", "brand": "Seasonic", "model": "FOCUS 650W",
     "performance_score": 82, "aesthetics_score": 60, "power_consumption": 0, "prices": [499]},
    {"name": "长城 550W", "component_type": "psu", "brand": "Great Wall", "model": "550W",
     "performance_score": 65, "aesthetics_score": 45, "prices": [269]},
    {"name": "鑫谷 750W 金牌", "component_type": "psu", "brand": "Sego", "model": "750W Gold",
     "performance_score": 78, "aesthetics_score": 65, "prices": [399]},
    # 机箱
    {"name": "联力 O11 Dynamic", "component_type": "case", "brand": "Lian Li", "model": "O11",
     "performance_score": 75, "aesthetics_score": 95, "rgb_support": True, "form_factor": "ATX", "prices": [599]},
    {"name": "乔思伯 D30", "component_type": "case", "brand": "Jonsbo", "model": "D30",
     "performance_score": 72, "aesthetics_score": 88, "form_factor": "mATX", "prices": [349]},
    {"name": "先马 平头哥", "component_type": "case", "brand": "Sama", "model": "平头哥",
     "performance_score": 60, "aesthetics_score": 50, "form_factor": "mATX", "prices": [129]},
    # 散热
    {"name": "利民 PA120", "component_type": "cooler", "brand": "Thermalright", "model": "PA120",
     "performance_score": 85, "aesthetics_score": 70, "prices": [149]},
    {"name": "九州风神 AK400", "component_type": "cooler", "brand": "Deepcool", "model": "AK400",
     "performance_score": 78, "aesthetics_score": 65, "prices": [89]},
    {"name": "乔思伯 CR1400", "component_type": "cooler", "brand": "Jonsbo", "model": "CR1400",
     "performance_score": 65, "aesthetics_score": 72, "prices": [59]},
    # 显示器
    {"name": "华硕 VG27AQ 27寸 2K 165Hz", "component_type": "monitor", "brand": "ASUS", "model": "VG27AQ",
     "performance_score": 85, "aesthetics_score": 75, "prices": [1699]},
    {"name": "小米 24.5寸 165Hz", "component_type": "monitor", "brand": "Xiaomi", "model": "24.5 165Hz",
     "performance_score": 72, "aesthetics_score": 80, "prices": [799]},
    {"name": "戴尔 U2422H 24寸", "component_type": "monitor", "brand": "Dell", "model": "U2422H",
     "performance_score": 70, "aesthetics_score": 85, "prices": [1299]},
]


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Component).limit(1))
        if result.scalar_one_or_none():
            print("已有数据，跳过 seed")
            return
        for item in SEED_COMPONENTS:
            prices = item.pop("prices")
            c = Component(**item)
            db.add(c)
            await db.flush()
            for pr in prices:
                p = Price(component_id=c.id, source="manual", price=float(pr))
                db.add(p)
        await db.commit()
        print("Seed 完成，共 %d 个组件" % len(SEED_COMPONENTS))


if __name__ == "__main__":
    asyncio.run(seed())
