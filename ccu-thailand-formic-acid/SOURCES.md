# แหล่งที่มาของตัวเลขทั้งหมด

ทุกตัวเลขที่สคริปต์ใช้อยู่ใน `params.py` และมีรหัส S.. ชี้มาที่ตารางนี้ (รันดูได้ด้วย `python3 params.py`)
ตัวเลขที่หาแหล่งสาธารณะไม่ได้ **ไม่ถูกใช้ในตัวเลขหลัก** และอยู่ในหัวข้อ "ต้องขอใบเสนอราคา" ด้านล่าง

**สถานะ**

| สัญลักษณ์ | ความหมาย |
|---|---|
| ✅ | อ่านจากเอกสารต้นฉบับแล้ว |
| 🔎 | มาจากข้อความในผลค้นหา (เครือข่ายที่ใช้ทำงานบล็อกการเปิด PDF หลายแห่ง) **ทีมต้องเปิดลิงก์ยืนยันก่อนใส่สไลด์** |
| 👥 | ข้อมูลหรือสมมติฐานที่ทีมหามาเอง ต้องแนบที่มาของทีม |
| 📐 | วิธีคำนวณมาตรฐาน ไม่ใช่ข้อมูล |

## ตารางแหล่งที่มา

| รหัส | ค่า | ตัวเลข | แหล่งที่มา | สถานะ |
|---|---|---|---|---|
| S01 | มวลโมเลกุล CO₂ / H₂ / HCOOH | 44.01 / 2.016 / 46.03 g/mol | ค่าน้ำหนักอะตอมมาตรฐาน IUPAC/CIAAW — [ciaaw.org](https://www.ciaaw.org/atomic-weights.htm) | ✅ |
| S02 | ค่าการปล่อย CO₂ ของก๊าซธรรมชาติ | 56.1 g CO₂/MJ (56,100 kg/TJ) | [2006 IPCC Guidelines Vol.2 Ch.2 Table 2.2](https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_2_Ch2_Stationary_Combustion.pdf) | 🔎 |
| S03 | กำลังผลิตโรงไฟฟ้าบางปะกง | 3,248 MW, ก๊าซธรรมชาติ | [egat.co.th/home/bangpakong-pp](https://www.egat.co.th/home/bangpakong-pp/) (ภาพหน้าจอจากทีม 24 ก.ย. 2569) | 👥 |
| S04 | แยกกลุ่มเครื่อง: MW / heat rate / CF | 1,386/5,600/0.65 · 710/7,500/0.45 · 1,152/10,500/0.15 | ไฟล์คำนวณของทีม: MW จาก กฟผ., heat rate จาก GE Vernova 9HA.02 และค่ามาตรฐาน, **CF เป็นสมมติฐานทางวิศวกรรมของทีม** | 👥 |
| S05 | องค์ประกอบไอเสียโรงไฟฟ้าก๊าซ (NGCC) | CO₂ ~4 vol%, O₂ ~12 vol% | [IEAGHG 2012/8](https://ieaghg.org/publications/2012-08%20CO2%20Capture%20at%20Gas%20Fired%20Power%20Plants.pdf), [NCCC: PZAS at NGCC conditions](https://www.nationalcarboncapturecenter.com/wp-content/uploads/2021/01/University-of-Texas-at-Austin-PZASTM-at-NGCC-Conditions-2019.pdf) | 🔎 |
| S06 | พลังงานไล่ CO₂ ของ MEA 30 wt% | 3.7 GJ/t CO₂ ที่ดักจับ 85% (งานอื่น 3.0–3.9) | Abu-Zahra et al. 2007, Int. J. Greenhouse Gas Control 1:37 — อ้างใน [Frontiers in Energy Research 2023](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2023.1230743/full) | 🔎 |
| S07 | MEA ที่ต้องเติมชดเชย (เสื่อม/สูญหาย) | 2.2 kg/t CO₂ (โรงงานนำร่องต่าง ๆ 0.21–3.65) | Strazisar et al. 2003, Energy & Fuels 17:1034; ช่วงค่าจาก [Ind. Eng. Chem. Res. 2022](https://pubs.acs.org/doi/10.1021/acs.iecr.2c02344), [OSTI 1485413](https://www.osti.gov/servlets/purl/1485413) | 🔎 |
| S08 | ต้นทุนดักจับ CO₂ ที่โรงไฟฟ้าก๊าซ F-class, ดักจับ 90% | 61 USD/t CO₂ (Rev 4a) · 80 USD/t (Rev 4) — ดอลลาร์ปี 2018, CF 85% | [NETL Baseline Rev 4a](https://netl.doe.gov/node/12161), [Carbon Herald](https://carbonherald.com/netl-updates-key-report-for-carbon-capture-costs-and-performance/) | 🔎 |
| S09 | ไฟฟ้าที่ PEM electrolyzer ใช้ | 51.2 kWh/kg H₂ (ปี 2020) | [IRENA 2020 Green hydrogen cost reduction](https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2020/Dec/IRENA_Green_hydrogen_cost_2020.pdf) | 🔎 |
| S10 | ค่าไฟฟ้าเฉลี่ยประเทศไทย | 3.95 บาท/หน่วย (ฐาน 3.78 + Ft 16.23 สต.) ก.ย.–ธ.ค. 2569 ไม่รวม VAT | [กกพ. เอกสารเผยแพร่ Ft ก.ย.–ธ.ค. 69](https://www.erc.or.th/web-upload/200xf869baf82be74c18cc110e974eea8d5c/tinymce/21-4763a2012e437a8e2cc87f4be44fa17e/FT/%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%AA%E0%B8%B2%E0%B8%A3%E0%B9%80%E0%B8%9C%E0%B8%A2%E0%B9%81%E0%B8%9E%E0%B8%A3%E0%B9%88-Ft-%E0%B8%87%E0%B8%A7%E0%B8%94-%E0%B8%81.%E0%B8%A2-%E0%B8%98.%E0%B8%84.69__Final.pdf), [MGR Online](https://mgronline.com/business/detail/9690000072165) | 🔎 |
| S11 | โรงงานกรดฟอร์มิกจาก CO₂ อ้างอิง (Case A: trihexylamine + Ru 250 ppm) | 13,030 t/yr, 99.78%; ลงทุน 26.743 M USD; ค่าดำเนินการ 15.386 M USD/yr; ต้นทุน 1.18 USD/kg; ราคาขายในงาน 1.40; ขั้นต่ำคุ้มทุน 1.36; CO₂ ~14 kt/yr; สัดส่วนค่าดำเนินการ: ค่าโรงงาน 22% แรงงาน 15% สาธารณูปโภค 25% วัตถุดิบ 36%; อายุโครงการ 15 ปี | Tzitzili et al. 2025, *Processes* 13:3626, [doi:10.3390/pr13113626](https://doi.org/10.3390/pr13113626) — Table 5, Table 6, หัวข้อ 3 (ไฟล์ `pdfs/05_Tzitzili2025_Processes.pdf`) หมายเหตุ: **ไม่รวมการดักจับ CO₂** และราคา H₂ อยู่ในตารางเสริม S16 ที่ไม่ได้อยู่ใน PDF | ✅ |
| S12 | อัตราแลกเปลี่ยน | 33.426 บาท/USD (24 ก.ย. 2569) | ธปท. อัตราถัวเฉลี่ยระหว่างธนาคาร — [กรุงเทพธุรกิจ](https://www.bangkokbiznews.com/finance/1253415), [bot.or.th](https://www.bot.or.th/th/statistics/exchange-rate.html) | 🔎 |
| S13 | ตลาดกรดฟอร์มิกโลก | 971.6 kt (2025) · อีกแหล่ง 1.10 Mt (2025) | [IMARC](https://www.imarcgroup.com/formic-acid-market-statistics), [Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/formic-acid-market) | 🔎 |
| S14 | มูลค่านำเข้ากรดฟอร์มิก HS 29151100 เดือน ม.ค. | 2566: 17.95 · 2567: 15.01 · 2568: 24.29 · 2569: 21.36 ล้านบาท (CIF) | ภาพหน้าจอสถิติการนำเข้าจากทีม — **ทีมต้องระบุชื่อเว็บไซต์/หน่วยงาน** | 👥 |
| S15 | ราคากรดฟอร์มิกที่เกษตรกรซื้อ | แกลลอน 5 กก. 240–380 บาท · ลัง 6 แกลลอน 1,570–1,800 บาท | ทีมสำรวจราคาร้านค้า — **ทีมต้องแนบชื่อร้าน/ลิงก์/วันที่** | 👥 |
| S16 | กฎ 0.6 (six-tenths rule) ปรับค่าลงทุนตามขนาด | ค่าลงทุน ∝ (ขนาด)^0.6 | Peters, Timmerhaus & West, *Plant Design and Economics for Chemical Engineers* (ตำราวิศวกรรมเคมีมาตรฐาน) | 📐 |
| S18 | ขนาดโรงงานและเกรดสินค้า | 10,000 t/yr กรด 85% (เกรดอุตสาหกรรมที่ขายให้สวนยาง) | การตัดสินใจออกแบบของทีม ขนาดเลือกให้ใกล้ปริมาณนำเข้า (ต้องยืนยันด้วยปริมาณนำเข้าจริงเป็น กก.) | 👥 |
| S19 | สภาวะการทำงาน MEA 30% | MEA เข้าหอดูดซับ 40 °C (อุตสาหกรรม 42–45 °C); MEA อิ่มออก 50–60 °C; อุ่นเป็น 100–110 °C; หอไล่ 115–125 °C, ~150 kPa; loading อิ่ม 0.5 / จาง 0.2 mol/mol | [Pilot-scale 30 wt% MEA (ScienceDirect 2023)](https://www.sciencedirect.com/science/article/pii/S030626192301557X), [Comparative Performance of 40% and 30% MEA](https://eprints.whiterose.ac.uk/id/eprint/155639/1/Comparative%20Performance%20of%2040%25%20and%2030%25%20MEA.pdf), [Stripper operating parameters (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1750583613000856) | 🔎 |
| S17 | LNG ของ กฟผ. สำหรับบางปะกง | ~1.2 Mt/yr (2566–2570) แปรสภาพที่ LNG มาบตาพุด แห่งที่ 2 แล้วส่งเป็นก๊าซทางท่อ | [EGAT 2023-10-03](https://www.egat.co.th/home/en/20231003e/), [The Nation](https://www.nationthailand.com/pr-news/pr-news/40044331) | 🔎 |

## ต้องขอใบเสนอราคา (ไม่มีแหล่งสาธารณะ ไม่ใช้ในตัวเลขหลัก)

| ค่า | ถามใคร |
|---|---|
| ปริมาณนำเข้าเป็น กก. (เพื่อหาราคา CIF ต่อ กก.) | เว็บสถิติเดียวกับ S14 เลือกแสดงปริมาณ |
| ราคาเอมีนตติยภูมิ (trihexylamine), MEA, ตัวเร่ง Ru | ผู้ขายสารเคมีในไทย |
| ราคาไอน้ำ / ต้นทุนผลิตไฟฟ้าของ กฟผ. ที่บางปะกง | กฟผ. |
| ค่าลงทุนของหน่วยดักจับขนาดเล็ก + PEM ~2 MW | ผู้ผลิตอุปกรณ์ |
| ค่ารถแทงก์ขนกรด | บริษัทขนส่งวัตถุอันตราย |
| ค่าเช่าพื้นที่/ส่วนแบ่งให้ กฟผ. | กฟผ. |
| ราคา H₂ ที่งาน Tzitzili ใช้ | ตารางเสริม S16–S19 ของงานวิจัย (ดาวน์โหลดจากหน้า doi) |

## เลิกใช้แล้ว

- **ความเย็นจาก LNG** (`cryo_capture.py`): บางปะกงไม่มี LNG เหลวในพื้นที่ (S17) ทีมตัดสินใจเลิกใช้ ก.ย. 2569
- **ตัวเลขต้นทุน 15.7 / 17.9 บาท/กก. เดิม**: มาจากราคาที่สมมติเอง ดูได้ที่ `python3 process_cost.py --assumed` แต่ห้ามใช้ในสไลด์
