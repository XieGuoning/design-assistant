# DRAENERT 产品型号、尺寸与官方 CAD／3D 下载索引

核验日期：2026-10-05。仅使用 DRAENERT 官网公开页面及其直接链接。

本项目的完整结构化索引已扩展到 78 个产品条目及 81 个 CAD／3DS 下载入口（75 个 DWG、6 个 3DS）。本文是配置和尺寸的精选参考；所有型号及当前采集结果以 `data/catalog.json` 和 `knowledge/catalog-index.md` 为入口。

本次后续复查：上述英文 Adler、Atlas、Paramount、Dan 数据表的直接 URL 在网页读取器中未能再次读取（裸域名和 www 都失败）；先前核实的尺寸保留作来源记录，回答现行尺寸时优先复核产品页及已归档的清晰数据表。Nobile Soft 和 Adler Outdoor 英文表已成功归档。失败不等同于厂家删除文件，不能承诺这些链接当前可访问。

## 回答边界

- “模型”可指产品型号，也可指 CAD／三维文件；应结合用户描述判断。用户已在本次会话确认两者均需要。
- 产品信息、可选石材、尺寸、伸缩状态和文件类型必须分别回答。产品型号相同不代表具体配置相同，例如 Adler 与 Adler Magnum 都显示 1224。
- 官网下载项名称已核实；下面的 ZIP 文件尚未下载或检查内部成员，因此不要把网页标注为 DWG 的 ZIP 直接称为已检查的二维图或三维图。DWG 本身不能证明模型是二维或三维。
- 页面公开展示下载入口，没有观察到这些入口要求账户登录；这不是对所有官网资源或未来访问状态的保证。
- 本次网页读取器不支持 ZIP 内容。`Unsupported content-type: application/zip` 是读取器限制，不等同于官网文件失效。超时意味着本次获取未成功，不能声称该文件一定存在或已经下载成功。
- 许多产品有 pCon 交互嵌入；读取到的通用入口为 <https://ui.pcon-solutions.com/>，提示需要 JavaScript。没有核验其导出格式、登录要求或完整产品配置，不要承诺可直接导出 SKP、MAX、OBJ、FBX、RVT 等格式。
- 返回文件时应说明来自官网、对应产品及具体尺寸／伸缩状态；用户需要其他格式时先检查真实文件或可用导出功能。

## 已核实分类入口

| 类别 | 官方入口 | 本次分类页中的不同产品链接数 |
|---|---|---:|
| 全部产品分类 | <https://draenert.de/de/produkte.html> | 5 类 |
| 餐桌 Esstische | <https://draenert.de/de/produkte/esstische.html> | 18 |
| 茶几／边几 Couchtische & Beistelltische | <https://draenert.de/de/produkte/couchtische-und-beistelltische.html> | 16 |
| 椅子／吧椅 Stühle & Barhocker | <https://draenert.de/de/produkte/stuehle-barhocker.html> | 19 |
| 户外 Outdoor | <https://draenert.de/de/produkte/outdoor.html> | 11 |
| Art Edition | <https://draenert.de/de/produkte/art-edition.html> | 14 |

链接数是当前分类页面的索引观察，不是可下载 CAD 文件数；不同型号、后缀或变体必须保留，不能仅按数值合并。Art Edition 抽查 Marble Wing 与 X1 / X2，没有在所读产品页面看到 CAD／3D 下载块，不能承诺全部产品都有模型。

## 已核实直接下载地址

下载地址直接来自相应产品页面的 Downloads 链接。状态：**读取器不支持 ZIP**＝获取响应被报告为 application/zip，但内部未检查；**获取超时**＝下载地址已从官方链接解析，本次读取未完成。

### Adler／Adler Magnum，1224

产品页：[Adler（英文）](https://www.draenert.de/en/products/dining-tables/adler.html)、[Adler Magnum（德文）](https://draenert.de/de/produkte/esstische/1224-adler-1.html)。本次两个产品页均标注 DWG 未伸展／可伸展版本；英文搜索结果曾标注 3DS，但当前读取的标准 Adler／德文 Magnum 页面没有 3DS 项，因此以当前页面为准。

| 官网下载项 | 直接文件 | 本次状态 |
|---|---|---|
| DWG table without extension | [1224_ohne_Auszug.zip](https://draenert.de/_Resources/Persistent/f/3/3/c/f33c090798871479e084c462494684e06f0348b5/1224_ohne_Auszug.zip) | 读取器不支持 ZIP |
| DWG table with extension | [1224_Adler_ausziehbar.zip](https://draenert.de/_Resources/Persistent/1/b/a/6/1ba6d9f96b9de5f71ba9b05d1a7146139e5df9de/1224_Adler_ausziehbar.zip) | 读取器不支持 ZIP |
| Productinformation | [Adler overview stone／wood／Conference，EN，1.5.26 PDF](https://draenert.de/_Resources/Persistent/3/5/7/c/357cdf8303ddbd8a0ed4abbaf2c2ed85b45cd5b2/1224_Adler_overview_stone_wood_Conference_EN_1.5.26.pdf) | PDF 文本可读，5 页 |

### Adler Outdoor，页面型号 1224，数据表型号 1224-O

产品页：[Adler Outdoor](https://draenert.de/en/products/outdoor/adler-outdoor.html)。页面标注 3DS 与 DWG；两份 ZIP 文件名指向不同尺寸，不能当作同一配置。

| 官网下载项 | 直接文件 | 本次状态 |
|---|---|---|
| 3ds-data | [1224_ZSB_fest_120x280cm_bo_Outdoor.zip](https://draenert.de/_Resources/Persistent/8/6/5/8/86580828927040bc41b95984ada43cb7726d3ceb/1224_ZSB_fest_120x280cm_bo_Outdoor.zip) | 读取器不支持 ZIP |
| dwg-data | [1224_ZSB_fest_105x200cm_bo_Outdoor_dwg.zip](https://draenert.de/_Resources/Persistent/2/d/b/9/2db9451e6f4c468030b411001630da6b26d7c0f9/1224_ZSB_fest_105x200cm_bo_Outdoor_dwg.zip) | 读取器不支持 ZIP |
| Productinformation | [1224-O Adler outdoor，EN，1.5.26 PDF](https://draenert.de/_Resources/Persistent/c/6/9/3/c693c337fc9c243cedb6fddfb93841aedc690009/1224-O_Adler_outdoor_EN_1.5.26.pdf) | PDF 文本可读，1 页 |

### Atlas，1280-II

产品页：[Atlas](https://draenert.de/en/products/dining-tables/1280-II-atlas.html)。页面保留型号后缀 II。下载项均标注 DWG。

| 官网下载项 | 直接文件 | 本次状态 |
|---|---|---|
| DWG without extension | [1280 Atlas Tisch ohne Auszug.zip](https://draenert.de/_Resources/Persistent/c/1/b/a/c1ba5b567acfbadd44a1367b9a043ae3cf55b3da/1280%20Atlas%20Tisch%20ohne%20Auszug.zip) | 读取器不支持 ZIP |
| DWG with extension | [1280 Atlas Tisch mit Auszug.zip](https://draenert.de/_Resources/Persistent/3/1/6/5/3165df27f7277dd035bb3266f4bbb546054cc8c7/1280%20Atlas%20Tisch%20mit%20Auszug.zip) | 获取超时 |
| Productinformation | [Atlas overview stone／wood，EN，1.5.26 PDF](https://draenert.de/_Resources/Persistent/4/c/0/b/4c0b5e9b623a074d8a1ddf49f62cd492f9b4e98b/1280_Atlas_overview_stone_wood_EN_1.5.26.pdf) | PDF 文本可读，5 页 |

### Paramount，1410

产品页：[Paramount](https://draenert.de/en/products/dining-tables/1410-Paramount.html)。单桌、组合双桌和 console 是分别提供的文件。

| 官网下载项 | 直接文件 | 本次状态 |
|---|---|---|
| DWG console | [1410 Paramount Konsole.zip](https://draenert.de/_Resources/Persistent/1/1/a/b/11ab94a1a731e082bf1e0349d1f2f467a88d1d47/1410%20Paramount%20Konsole.zip) | 读取器不支持 ZIP |
| DWG single table | [1410-Paramount Einzeltisch.zip](https://draenert.de/_Resources/Persistent/0/b/3/1/0b31831c98715ee89d807b206673e14e652f9648/1410-Paramount%20Einzeltisch.zip) | 读取器不支持 ZIP |
| DWG double table | [1410-Paramount Doppeltisch.zip](https://draenert.de/_Resources/Persistent/9/d/a/f/9daf8ac956b66cdd3a29317d130a78e488bab0db/1410-Paramount%20Doppeltisch.zip) | 获取超时 |
| Productinformation | [Paramount，EN，1.5.26 PDF](https://draenert.de/_Resources/Persistent/c/0/a/0/c0a064e6ed5a28887981f051963bab419ea400c2/1410_Paramount_EN_1.5.26.pdf) | PDF 文本可读，2 页 |

### Move，1372

产品页：[Move](https://draenert.de/en/products/coffee-and-side-tables/1372-move-1.html)。

2026-10-05 复查补充：图片石材、两档尺寸和当前可读取的新闻中心资料见 [MOVE 1372 专项记录](move-1372.md)。具体尺寸来自销售商公开规格，官方数据表本次文字乱码；不要将销售商数字描述为已经从清晰官方表格读取。

| 官网下载项 | 直接文件 | 本次状态 |
|---|---|---|
| dwg-Daten | [1372-Move.zip](https://draenert.de/_Resources/Persistent/a/7/d/5/a7d52c0e8c951114bc2ea5117e2ccbfdcc2ff6b1/1372-Move.zip) | 获取超时 |
| Produktinformation（德文页） | [Move，DE，1.5.26 PDF](https://draenert.de/_Resources/Persistent/5/9/6/7/59676beab0d5bdb6672b076c78bf89553dc98d2a/1372_Move_DE_1.5.26.pdf) | 初次返回 PDF，随后复查 404；不能保证地址有效，宜从产品页再次解析 |

### Dan Kreuz／Dan Cross Base，2043

产品页：[Dan Cross Base](https://draenert.de/en/products/chairs-and-bar-stools/2043-dan.html)。

| 官网下载项 | 直接文件 | 本次状态 |
|---|---|---|
| dwg-data | [2043_DAN.zip](https://draenert.de/_Resources/Persistent/d/7/b/2/d7b2b6eab1d0abcf67eb2ffd1c1cccab0b11b41a/2043_DAN.zip) | 读取器不支持 ZIP |
| Productinformation | [Dan，EN，1.5.26 PDF](https://draenert.de/_Resources/Persistent/d/1/3/f/d13fb152a61335272b35479a2f98fc47cae93cb8/2043_Dan_EN_1.5.26.pdf) | PDF 文本可读，2 页 |

### Nobile Soft，2076

产品页：[Nobile Soft](https://draenert.de/de/produkte/stuehle-barhocker/2076-nobile-soft.html)。

| 官网下载项 | 直接文件 | 本次状态 |
|---|---|---|
| dwg-Daten | [2076_NOBILE.zip](https://draenert.de/_Resources/Persistent/c/d/a/4/cda4bdf35f5ec8a963650c85953726f63d5e4c79/2076_NOBILE.zip) | 获取超时 |
| Productinformation | [Nobile Soft，EN，1.5.26 PDF](https://draenert.de/_Resources/Persistent/6/6/0/0/66006f8a117954f6d61dc5ccc1d836f5476c64c9/2076_Nobile%20Soft_EN_1.5.26.pdf) | PDF 文本可读，2 页 |

### Nobile Bar Soft，2078-V／2078-VI

详见 [2078 专项记录](nobile-bar-2078.md)。英文官方数据表核实 V 座高 65 cm、VI 座高 75 cm；现有 CAD 包名为 `2078_VI_NOBILE_BAR.zip`，不能直接当作 V 专用模型。

### 更多户外模型下载入口

| 产品／型号 | 官方产品页 | 官方标注格式／直接文件 | 本次状态 |
|---|---|---|---|
| Atlas Outdoor／1280 | [产品页](https://draenert.de/de/produkte/outdoor/atlas-outdoor.html) | 3DS：[1280-II_ZSB_3ds.zip](https://draenert.de/_Resources/Persistent/a/7/e/3/a7e39f2b1df497cde6a84dc49eeffdcfbe46f9a0/1280-II_ZSB_3ds.zip) | 获取超时 |
| Atlas Outdoor／1280 | 同上 | DWG：[1280-II_ZSB_dwg.zip](https://draenert.de/_Resources/Persistent/3/8/3/a/383aa022eaaf41db7e408e8e022064f33e5f290a/1280-II_ZSB_dwg.zip) | 读取器不支持 ZIP |
| Qbic Outdoor／1365 | [产品页](https://draenert.de/de/produkte/outdoor/qbic-outdoor.html) | 3DS：[1365_3DS-Daten.zip](https://draenert.de/_Resources/Persistent/2/b/5/a/2b5a97ecde87ff8e1d05c095cf3733d20921f141/1365_3DS-Daten.zip) | 获取超时 |
| Qbic Outdoor／1365 | 同上 | DWG：[1365_DWG-Daten.zip](https://draenert.de/_Resources/Persistent/d/d/a/7/dda7426c485cd13057198af714a2b3eeb46d9c61/1365_DWG-Daten.zip) | 读取器不支持 ZIP |
| Tosca Outdoor／1380 | [产品页](https://draenert.de/de/produkte/outdoor/tosca-outdoor.html) | 3DS：[1380-ZSB-3ds.zip](https://draenert.de/_Resources/Persistent/3/a/f/b/3afb7620f945e079517fd9e264ae53c938722039/1380-ZSB-3ds.zip) | 读取器不支持 ZIP |
| Tosca Outdoor／1380 | 同上 | DWG：[1380-ZSB-dwg.zip](https://draenert.de/_Resources/Persistent/9/a/1/5/9a15a536d81d495dfb669295f6ae286804d0cca2/1380-ZSB-dwg.zip) | 获取超时 |
| Lou／3025-O | [产品页](https://draenert.de/de/produkte/outdoor/lou.html) | DWG：[3025_O_LOU_mit und ohne_Kissen.zip](https://draenert.de/_Resources/Persistent/9/b/e/7/9be71e53a0079f88ea4d96764b7fa5e34f3480b1/3025_O_LOU_mit%20und%20ohne_Kissen.zip) | 读取器不支持 ZIP |

## 已核实尺寸事实

以下餐桌尺寸按官网 **宽 × 长 × 高（W × L × H），单位 cm，近似值** 保存。椅子按 **宽 × 深 × 高（W × D × H）** 保存。中文回答如改用“长 × 宽”，必须交换前两项。

| 产品 | 尺寸／选项 | 证据 |
|---|---|---|
| Adler 1224，天然石，不伸缩 | 95 × 160 × 73；105 × 180／200／220／240／260 × 73 | 上述 Adler EN PDF 第 3 页 |
| Adler 1224，天然石，可伸缩 | 95 × 150 → 210 × 74.5；105 × 170 → 250 × 74.5；105 × 190 → 270 × 74.5 | 同上第 3 页；箭头仅表示长度变化 |
| Adler Magnum 1224，天然石 | 固定 120 × 260／280 × 73.5；伸缩 120 × 270 → 370 × 75 | 同上第 3 页；木材版本应另看第 4 页 |
| Adler Outdoor 1224-O，天然石 | 固定 95 × 160 × 73；105 × 180／200／220／240／260 × 73；Magnum 120 × 260／280 × 73.5 | 上述 Adler Outdoor EN PDF 第 1 页 |
| Atlas 1280-II，天然石，可伸缩 | 92 × 160 → 233 × 75；105 × 180 → 260 × 75；105 × 200 → 280 × 75 | 上述 Atlas EN PDF 第 3 页 |
| Atlas Magnum，天然石，可伸缩 | 105 × 240 → 320 × 75；105 × 280 → 360 × 75 | 同上第 3 页；数据表注明这些 Magnum 版本纹理不连续 |
| Paramount 1410，单桌 | 110 × 240 × 74；120 × 280 × 74 | 上述 Paramount EN PDF 第 2 页 |
| Paramount 1410，组合双桌 | 130 × 350／440／560 × 74 | 同上第 2 页 |
| Paramount 1410，console | 50 × 177 × 74 | 同上第 2 页 |
| Dan Cross Base 2043 | 59 × 60 × 82.5；座高 48，座深 45 | 上述 Dan EN PDF 第 2 页；带自动回位功能时闲置高度约高 1.5 cm |
| Nobile Soft 2076 | 48 × 54 × 87.5；座高 47.5，座深 44 | 上述 Nobile Soft EN PDF 第 2 页 |
| Nobile Soft 2076-I | 55 × 54 × 87.5；扶手高 68 | 同上第 2 页 |
| Nobile Soft X 2076-X | 46 × 54 × 87.5；窄靠背宽 39.5 | 同上第 2 页 |
| Nobile Soft X 扶手版 2076-X-I | 55 × 54 × 87.5；扶手高 68 | 同上第 2 页 |

Adler 与 Atlas 的尺寸依固定／伸缩、石材／木材、Magnum 及底座配置变化。不能把以上任一尺寸推广为整个型号的唯一尺寸。个性化／会议桌尺寸在 PDF 中说明可询价定制，不能承诺任意尺寸都能立即下载对应模型。

## 可用的材料搭配证据

- 标准 Adler 产品页明确展示 Sodalith、Azul Mary、Dreaming Green 等石材实例，但这些示例不代表对应 ZIP 含有该石材纹理贴图。
- Paramount 产品页明确展示 Palomino Blue；可作为蓝色系石材与家具组合的官方实例。
- Tosca Outdoor 产品页明确展示 Azul Aquarella；判断户外适用性仍应读取石材自身资料及对应产品数据表。

## 查找、返回和维护方法

1. 以产品名称、完整型号及后缀检索产品索引；确认室内／户外、固定／伸缩、单桌／双桌、扶手／无扶手等配置。
2. 产品资料回答给出名称、型号、用途、材料选项、已核实尺寸、产品页与数据表链接。
3. 文件请求优先给官方直接文件链接；标明官网标注格式和当前获取状态。需要实际附件时下载到本地、检查 ZIP 成员和尺寸，再提供相应文件。
4. 若没有目标格式，说明已发现的官方格式。不要把重建或转换的文件描述为厂家原始模型。
5. 更新时重新读取产品页的 Downloads 链接，避免只凭旧的 Persistent URL；网页和 PDF 有冲突时保留两条证据，说明差异，必要时以现行数据表复核。
