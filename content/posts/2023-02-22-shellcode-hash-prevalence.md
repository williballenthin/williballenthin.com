---
title: "shellcode hash prevalence"
date: 2023-02-22T00:00:00-07:00
tags:
  - python
  - reverse-engineering
  - malware-analysis
  - shellcode
  - virustotal
  - yara
---

In [capa-rules#175](https://github.com/mandiant/capa-rules/issues/175) we want to know which shellcode hashes are commonly seen. Let's use VirusTotal to estimate the prevalence of the hashing algorithms. 

TL;DR:

  - `crc32`: 20+
  - `poisonIvyHash`: 9
  - `rol7XorHash32`: 5
  - `addRor13Hash32`: 4
  - `ror13AddWithNullHash32`: 4
  - `chAddRol8Hash32`: 2
  - `ror7AddHash32`: 2
  - `sll1AddHash32`: 2
  - `add1505Shl5Hash32`: 1
  - `hash_Carbanak`: 1
  - `ror13AddHash32`: 1

Using the [flare-ida](https://github.com/mandiant/flare-ida) [shellcode hashes database](https://github.com/mandiant/flare-ida/tree/master/shellcode_hashes) `sc_hashes.db`, we can generate VirusTotal queries to search for PE files with interesting hashes:

```py
import urllib
import sqlite3
import binascii
import collections

db = sqlite3.connect("sc_hashes.db")
conn = db.cursor()
cursor = conn.execute('''
  SELECT symbol_name, hash_name, hash_size, hash_val 
  FROM symbol_hashes
  INNER JOIN hash_types ON symbol_hashes.hash_type = hash_types.hash_type
  WHERE symbol_name IN (
    "VirtualAlloc", 
    "VirtualProtect", 
    "CreateRemoteThread", 
    "WriteProcessMemory"
  )
  ORDER BY symbol_name, hash_name;
''')

hashes = collections.defaultdict(dict)
for symbol_name, hash_name, hash_size, hash_val in cursor.fetchall():
    assert hash_size == 32
    hashes[hash_name][symbol_name] = hash_val
    
for hash_name, symbols in sorted(hashes.items()):
    print(f"{hash_name}")
    
    query = []
    for symbol_name, hash_val in sorted(symbols.items()):   
        print(f"  {symbol_name:<24} {hex(hash_val)}")
        
        content = binascii.hexlify(hash_val.to_bytes(4, "little")).decode("ascii").upper()
        
        query.append(f'content: {{ {content} }}')
        
    query = " and ".join(query)
    query = f"({query})"
    query += " and size:100kb- and (tag:pedll or tag:peexe)"
    url = f"https://www.virustotal.com/gui/search/{urllib.parse.quote(query)}/files"
        
    print(f"  {query}")
    print(f"  {url}")
    
    print()
```

results:

`add1505Shl5Hash32`
  - `CreateRemoteThread`: 0xAA30775D
  - `VirtualAlloc`: 0x382C0F97
  - `VirtualProtect`: 0x844FF18D
  - `WriteProcessMemory`: 0x6F22E8C8
  - `(content: { 5D7730AA } and content: { 970F2C38 } and content: { 8DF14F84 } and content: { C8E8226F }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%205D7730AA%20%7D%20and%20content%3A%20%7B%20970F2C38%20%7D%20and%20content%3A%20%7B%208DF14F84%20%7D%20and%20content%3A%20%7B%20C8E8226F%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 1

`addRol5HashOncemore32`
  - `CreateRemoteThread`: 0xC7D1B1C8
  - `VirtualAlloc`: 0xE9D81123
  - `VirtualProtect`: 0x2A97EED8
  - `WriteProcessMemory`: 0x99E4F69A
  - `(content: { C8B1D1C7 } and content: { 2311D8E9 } and content: { D8EE972A } and content: { 9AF6E499 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20C8B1D1C7%20%7D%20and%20content%3A%20%7B%202311D8E9%20%7D%20and%20content%3A%20%7B%20D8EE972A%20%7D%20and%20content%3A%20%7B%209AF6E499%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`addRor13Hash32`
  - `CreateRemoteThread`: 0xE6EB95EC
  - `VirtualAlloc`: 0x52A48D7E
  - `VirtualProtect`: 0x30DBCA36
  - `WriteProcessMemory`: 0x550EC1EB
  - `(content: { EC95EBE6 } and content: { 7E8DA452 } and content: { 36CADB30 } and content: { EBC10E55 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20EC95EBE6%20%7D%20and%20content%3A%20%7B%207E8DA452%20%7D%20and%20content%3A%20%7B%2036CADB30%20%7D%20and%20content%3A%20%7B%20EBC10E55%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 4

`addRor13HashOncemore32`
  - `CreateRemoteThread`: 0xAF67375C
  - `VirtualAlloc`: 0x6BF29524
  - `VirtualProtect`: 0x51B186DE
  - `WriteProcessMemory`: 0xF5AA876
  - `(content: { 5C3767AF } and content: { 2495F26B } and content: { DE86B151 } and content: { 76A85A0F }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%205C3767AF%20%7D%20and%20content%3A%20%7B%202495F26B%20%7D%20and%20content%3A%20%7B%20DE86B151%20%7D%20and%20content%3A%20%7B%2076A85A0F%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`addRor4WithNullHash32`
  - `CreateRemoteThread`: 0xD6D70953
  - `VirtualAlloc`: 0x25E16828
  - `VirtualProtect`: 0xA25834D7
  - `WriteProcessMemory`: 0x23ACB005
  - `(content: { 5309D7D6 } and content: { 2868E125 } and content: { D73458A2 } and content: { 05B0AC23 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%205309D7D6%20%7D%20and%20content%3A%20%7B%202868E125%20%7D%20and%20content%3A%20%7B%20D73458A2%20%7D%20and%20content%3A%20%7B%2005B0AC23%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`adler32_666`
  - `CreateRemoteThread`: 0x608C07D2
  - `VirtualAlloc`: 0x36FC062C
  - `VirtualProtect`: 0x44E406E2
  - `WriteProcessMemory`: 0x6320081D
  - `(content: { D2078C60 } and content: { 2C06FC36 } and content: { E206E444 } and content: { 1D082063 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20D2078C60%20%7D%20and%20content%3A%20%7B%202C06FC36%20%7D%20and%20content%3A%20%7B%20E206E444%20%7D%20and%20content%3A%20%7B%201D082063%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`chAddRol8Hash32`
  - `CreateRemoteThread`: 0x4D761260
  - `VirtualAlloc`: 0xA7E6B43
  - `VirtualProtect`: 0x73B5E37
  - `WriteProcessMemory`: 0x72793A67
  - `(content: { 6012764D } and content: { 436B7E0A } and content: { 375E3B07 } and content: { 673A7972 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%206012764D%20%7D%20and%20content%3A%20%7B%20436B7E0A%20%7D%20and%20content%3A%20%7B%20375E3B07%20%7D%20and%20content%3A%20%7B%20673A7972%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 2

`crc32`
  - `CreateRemoteThread`: 0xFF808C10
  - `VirtualAlloc`: 0x9CE0D4A
  - `VirtualProtect`: 0x10066F2F
  - `WriteProcessMemory`: 0x4F58972E
  - `(content: { 108C80FF } and content: { 4A0DCE09 } and content: { 2F6F0610 } and content: { 2E97584F }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20108C80FF%20%7D%20and%20content%3A%20%7B%204A0DCE09%20%7D%20and%20content%3A%20%7B%202F6F0610%20%7D%20and%20content%3A%20%7B%202E97584F%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 20+

`crc32Xor0xca9d4d4e`
  - `CreateRemoteThread`: 0x351DC15E
  - `VirtualAlloc`: 0xC3534004
  - `VirtualProtect`: 0xDA9B2261
  - `WriteProcessMemory`: 0x85C5DA60
  - `(content: { 5EC11D35 } and content: { 044053C3 } and content: { 61229BDA } and content: { 60DAC585 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%205EC11D35%20%7D%20and%20content%3A%20%7B%20044053C3%20%7D%20and%20content%3A%20%7B%2061229BDA%20%7D%20and%20content%3A%20%7B%2060DAC585%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`crc32bzip2lower`
  - `CreateRemoteThread`: 0xDC726CA0
  - `VirtualAlloc`: 0x9A1DE93C
  - `VirtualProtect`: 0x1EE8630D
  - `WriteProcessMemory`: 0x70E16781
  - `(content: { A06C72DC } and content: { 3CE91D9A } and content: { 0D63E81E } and content: { 8167E170 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20A06C72DC%20%7D%20and%20content%3A%20%7B%203CE91D9A%20%7D%20and%20content%3A%20%7B%200D63E81E%20%7D%20and%20content%3A%20%7B%208167E170%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`dualaccModFFF1Hash`
  - `CreateRemoteThread`: 0x42AA0719
  - `VirtualAlloc`: 0x1F7004D3
  - `VirtualProtect`: 0x2B0605C9
  - `WriteProcessMemory`: 0x451E0764
  - `(content: { 1907AA42 } and content: { D304701F } and content: { C905062B } and content: { 64071E45 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%201907AA42%20%7D%20and%20content%3A%20%7B%20D304701F%20%7D%20and%20content%3A%20%7B%20C905062B%20%7D%20and%20content%3A%20%7B%2064071E45%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`fnv1Xor67f`
  - `CreateRemoteThread`: 0xC398C21C
  - `VirtualAlloc`: 0x328537E
  - `VirtualProtect`: 0x8206278C
  - `WriteProcessMemory`: 0xC0088895
  - `(content: { 1CC298C3 } and content: { 7E532803 } and content: { 8C270682 } and content: { 958808C0 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%201CC298C3%20%7D%20and%20content%3A%20%7B%207E532803%20%7D%20and%20content%3A%20%7B%208C270682%20%7D%20and%20content%3A%20%7B%20958808C0%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`hash_Carbanak`
  - `CreateRemoteThread`: 0x48B1574
  - `VirtualAlloc`: 0x3D8CAE3
  - `VirtualProtect`: 0x72D1864
  - `WriteProcessMemory`: 0x648B099
  - `(content: { 74158B04 } and content: { E3CAD803 } and content: { 64182D07 } and content: { 99B04806 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%2074158B04%20%7D%20and%20content%3A%20%7B%20E3CAD803%20%7D%20and%20content%3A%20%7B%2064182D07%20%7D%20and%20content%3A%20%7B%2099B04806%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 1

`hash_ror13AddUpperDllnameHash32`
  - `CreateRemoteThread`: 0xE0E966F4
  - `VirtualAlloc`: 0xFFDB946B
  - `VirtualProtect`: 0xE7729032
  - `WriteProcessMemory`: 0x466934B8
  - `(content: { F466E9E0 } and content: { 6B94DBFF } and content: { 329072E7 } and content: { B8346946 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20F466E9E0%20%7D%20and%20content%3A%20%7B%206B94DBFF%20%7D%20and%20content%3A%20%7B%20329072E7%20%7D%20and%20content%3A%20%7B%20B8346946%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`imul21hAddHash32`
  - `CreateRemoteThread`: 0x252B157D
  - `VirtualAlloc`: 0x97BC257
  - `VirtualProtect`: 0xE857500D
  - `WriteProcessMemory`: 0xB7930AE8
  - `(content: { 7D152B25 } and content: { 57C27B09 } and content: { 0D5057E8 } and content: { E80A93B7 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%207D152B25%20%7D%20and%20content%3A%20%7B%2057C27B09%20%7D%20and%20content%3A%20%7B%200D5057E8%20%7D%20and%20content%3A%20%7B%20E80A93B7%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`imul83hAdd`
  - `CreateRemoteThread`: 0x71469C9C
  - `VirtualAlloc`: 0xDE893462
  - `VirtualProtect`: 0x6C6EC404
  - `WriteProcessMemory`: 0xA11BEA85
  - `(content: { 9C9C4671 } and content: { 623489DE } and content: { 04C46E6C } and content: { 85EA1BA1 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%209C9C4671%20%7D%20and%20content%3A%20%7B%20623489DE%20%7D%20and%20content%3A%20%7B%2004C46E6C%20%7D%20and%20content%3A%20%7B%2085EA1BA1%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`mult21AddHash32`
  - `CreateRemoteThread`: 0x4B892318
  - `VirtualAlloc`: 0xDF894B12
  - `VirtualProtect`: 0x77E9F7C8
  - `WriteProcessMemory`: 0x107B9483
  - `(content: { 1823894B } and content: { 124B89DF } and content: { C8F7E977 } and content: { 83947B10 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%201823894B%20%7D%20and%20content%3A%20%7B%20124B89DF%20%7D%20and%20content%3A%20%7B%20C8F7E977%20%7D%20and%20content%3A%20%7B%2083947B10%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`or21hXorRor11Hash32`
  - `CreateRemoteThread`: 0xDF8469B4
  - `VirtualAlloc`: 0x8C552DB6
  - `VirtualProtect`: 0x74631D3F
  - `WriteProcessMemory`: 0x8F022E10
  - `(content: { B46984DF } and content: { B62D558C } and content: { 3F1D6374 } and content: { 102E028F }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20B46984DF%20%7D%20and%20content%3A%20%7B%20B62D558C%20%7D%20and%20content%3A%20%7B%203F1D6374%20%7D%20and%20content%3A%20%7B%20102E028F%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`or23hXorRor17Hash32`
  - `CreateRemoteThread`: 0xBAE620A4
  - `VirtualAlloc`: 0x8858D78F
  - `VirtualProtect`: 0x29AD5932
  - `WriteProcessMemory`: 0x6146132C
  - `(content: { A420E6BA } and content: { 8FD75888 } and content: { 3259AD29 } and content: { 2C134661 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20A420E6BA%20%7D%20and%20content%3A%20%7B%208FD75888%20%7D%20and%20content%3A%20%7B%203259AD29%20%7D%20and%20content%3A%20%7B%202C134661%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`playWith0xe8677835Hash`
  - `CreateRemoteThread`: 0xD4632723
  - `VirtualAlloc`: 0xE763FDF1
  - `VirtualProtect`: 0xB41F905F
  - `WriteProcessMemory`: 0xB2128ABF
  - `(content: { 232763D4 } and content: { F1FD63E7 } and content: { 5F901FB4 } and content: { BF8A12B2 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20232763D4%20%7D%20and%20content%3A%20%7B%20F1FD63E7%20%7D%20and%20content%3A%20%7B%205F901FB4%20%7D%20and%20content%3A%20%7B%20BF8A12B2%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`poisonIvyHash`
  - `CreateRemoteThread`: 0xCF4A7F65
  - `VirtualAlloc`: 0x4402890E
  - `VirtualProtect`: 0x79C3D4BB
  - `WriteProcessMemory`: 0xE9BBAD5
  - `(content: { 657F4ACF } and content: { 0E890244 } and content: { BBD4C379 } and content: { D5BA9B0E }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20657F4ACF%20%7D%20and%20content%3A%20%7B%200E890244%20%7D%20and%20content%3A%20%7B%20BBD4C379%20%7D%20and%20content%3A%20%7B%20D5BA9B0E%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 9

`rol3XorEax`
  - `CreateRemoteThread`: 0xDBA7F9E2
  - `VirtualAlloc`: 0xFFE3C3DE
  - `VirtualProtect`: 0xA99CA9EB
  - `WriteProcessMemory`: 0xEF430666
  - `(content: { E2F9A7DB } and content: { DEC3E3FF } and content: { EBA99CA9 } and content: { 660643EF }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20E2F9A7DB%20%7D%20and%20content%3A%20%7B%20DEC3E3FF%20%7D%20and%20content%3A%20%7B%20EBA99CA9%20%7D%20and%20content%3A%20%7B%20660643EF%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`rol3XorHash32`
  - `CreateRemoteThread`: 0x4A5F66C2
  - `VirtualAlloc`: 0xAB16D0AE
  - `VirtualProtect`: 0xC5FF2F46
  - `WriteProcessMemory`: 0xB04AD555
  - `(content: { C2665F4A } and content: { AED016AB } and content: { 462FFFC5 } and content: { 55D54AB0 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20C2665F4A%20%7D%20and%20content%3A%20%7B%20AED016AB%20%7D%20and%20content%3A%20%7B%20462FFFC5%20%7D%20and%20content%3A%20%7B%2055D54AB0%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`rol5AddHash32`
  - `CreateRemoteThread`: 0x7231F46C
  - `VirtualAlloc`: 0x48FA7604
  - `VirtualProtect`: 0xB60AA5FB
  - `WriteProcessMemory`: 0xA6A6793D
  - `(content: { 6CF43172 } and content: { 0476FA48 } and content: { FBA50AB6 } and content: { 3D79A6A6 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%206CF43172%20%7D%20and%20content%3A%20%7B%200476FA48%20%7D%20and%20content%3A%20%7B%20FBA50AB6%20%7D%20and%20content%3A%20%7B%203D79A6A6%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`rol5XorHash32`
  - `CreateRemoteThread`: 0xCA306453
  - `VirtualAlloc`: 0xA48D8A33
  - `VirtualProtect`: 0x4A155A82
  - `WriteProcessMemory`: 0x2A466170
  - `(content: { 536430CA } and content: { 338A8DA4 } and content: { 825A154A } and content: { 7061462A }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20536430CA%20%7D%20and%20content%3A%20%7B%20338A8DA4%20%7D%20and%20content%3A%20%7B%20825A154A%20%7D%20and%20content%3A%20%7B%207061462A%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`rol7AddHash32`
  - `CreateRemoteThread`: 0x46902C89
  - `VirtualAlloc`: 0x929199C0
  - `VirtualProtect`: 0x971112C8
  - `WriteProcessMemory`: 0x9CA4F7AC
  - `(content: { 892C9046 } and content: { C0999192 } and content: { C8121197 } and content: { ACF7A49C }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20892C9046%20%7D%20and%20content%3A%20%7B%20C0999192%20%7D%20and%20content%3A%20%7B%20C8121197%20%7D%20and%20content%3A%20%7B%20ACF7A49C%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`rol7AddXor2Hash32`
  - `CreateRemoteThread`: 0x73727A24
  - `VirtualAlloc`: 0xB4D5E14D
  - `VirtualProtect`: 0x69755A3B
  - `WriteProcessMemory`: 0xCDFE3245
  - `(content: { 247A7273 } and content: { 4DE1D5B4 } and content: { 3B5A7569 } and content: { 4532FECD }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20247A7273%20%7D%20and%20content%3A%20%7B%204DE1D5B4%20%7D%20and%20content%3A%20%7B%203B5A7569%20%7D%20and%20content%3A%20%7B%204532FECD%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`rol7XorHash32`
  - `CreateRemoteThread`: 0xE61874B3
  - `VirtualAlloc`: 0x697A6AFE
  - `VirtualProtect`: 0xA9DE6F5A
  - `WriteProcessMemory`: 0xBEA0BF35
  - `(content: { B37418E6 } and content: { FE6A7A69 } and content: { 5A6FDEA9 } and content: { 35BFA0BE }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20B37418E6%20%7D%20and%20content%3A%20%7B%20FE6A7A69%20%7D%20and%20content%3A%20%7B%205A6FDEA9%20%7D%20and%20content%3A%20%7B%2035BFA0BE%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 5

`rol8Xor0xB0D4D06Hash32`
  - `CreateRemoteThread`: 0x30427641
  - `VirtualAlloc`: 0xC61E6D49
  - `VirtualProtect`: 0x192F1259
  - `WriteProcessMemory`: 0x30B4669E
  - `(content: { 41764230 } and content: { 496D1EC6 } and content: { 59122F19 } and content: { 9E66B430 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%2041764230%20%7D%20and%20content%3A%20%7B%20496D1EC6%20%7D%20and%20content%3A%20%7B%2059122F19%20%7D%20and%20content%3A%20%7B%209E66B430%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`rol9AddHash32`
  - `CreateRemoteThread`: 0x14B23D4C
  - `VirtualAlloc`: 0x9EE2D962
  - `VirtualProtect`: 0x9154022F
  - `WriteProcessMemory`: 0x7E642835
  - `(content: { 4C3DB214 } and content: { 62D9E29E } and content: { 2F025491 } and content: { 3528647E }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%204C3DB214%20%7D%20and%20content%3A%20%7B%2062D9E29E%20%7D%20and%20content%3A%20%7B%202F025491%20%7D%20and%20content%3A%20%7B%203528647E%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`rol9XorHash32`
  - `CreateRemoteThread`: 0xD4F04BD4
  - `VirtualAlloc`: 0x5D192CFB
  - `VirtualProtect`: 0x6FB67220
  - `WriteProcessMemory`: 0xEB64101F
  - `(content: { D44BF0D4 } and content: { FB2C195D } and content: { 2072B66F } and content: { 1F1064EB }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20D44BF0D4%20%7D%20and%20content%3A%20%7B%20FB2C195D%20%7D%20and%20content%3A%20%7B%202072B66F%20%7D%20and%20content%3A%20%7B%201F1064EB%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`ror11AddHash32`
  - `CreateRemoteThread`: 0x7130F56D
  - `VirtualAlloc`: 0x973F27BF
  - `VirtualProtect`: 0x492F12D7
  - `WriteProcessMemory`: 0x3231CC1
  - `(content: { 6DF53071 } and content: { BF273F97 } and content: { D7122F49 } and content: { C11C2303 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%206DF53071%20%7D%20and%20content%3A%20%7B%20BF273F97%20%7D%20and%20content%3A%20%7B%20D7122F49%20%7D%20and%20content%3A%20%7B%20C11C2303%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`ror13AddHash32`
  - `CreateRemoteThread`: 0x72BD9CDD
  - `VirtualAlloc`: 0x91AFCA54
  - `VirtualProtect`: 0x7946C61B
  - `WriteProcessMemory`: 0xD83D6AA1
  - `(content: { DD9CBD72 } and content: { 54CAAF91 } and content: { 1BC64679 } and content: { A16A3DD8 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20DD9CBD72%20%7D%20and%20content%3A%20%7B%2054CAAF91%20%7D%20and%20content%3A%20%7B%201BC64679%20%7D%20and%20content%3A%20%7B%20A16A3DD8%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 1

`ror13AddHash32AddDll`
  - `CreateRemoteThread`: 0x799AACC6
  - `VirtualAlloc`: 0xE553A458
  - `VirtualProtect`: 0xC38AE110
  - `WriteProcessMemory`: 0xE7BDD8C5
  - `(content: { C6AC9A79 } and content: { 58A453E5 } and content: { 10E18AC3 } and content: { C5D8BDE7 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20C6AC9A79%20%7D%20and%20content%3A%20%7B%2058A453E5%20%7D%20and%20content%3A%20%7B%2010E18AC3%20%7D%20and%20content%3A%20%7B%20C5D8BDE7%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`ror13AddHash32DllSimple`
  - `CreateRemoteThread`: 0xE0E966F4
  - `VirtualAlloc`: 0xFFDB946B
  - `VirtualProtect`: 0xE7729032
  - `WriteProcessMemory`: 0x466934B8
  - `(content: { F466E9E0 } and content: { 6B94DBFF } and content: { 329072E7 } and content: { B8346946 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20F466E9E0%20%7D%20and%20content%3A%20%7B%206B94DBFF%20%7D%20and%20content%3A%20%7B%20329072E7%20%7D%20and%20content%3A%20%7B%20B8346946%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`ror13AddHash32Sub1`
  - `CreateRemoteThread`: 0x72BD9CDC
  - `VirtualAlloc`: 0x91AFCA53
  - `VirtualProtect`: 0x7946C61A
  - `WriteProcessMemory`: 0xD83D6AA0
  - `(content: { DC9CBD72 } and content: { 53CAAF91 } and content: { 1AC64679 } and content: { A06A3DD8 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20DC9CBD72%20%7D%20and%20content%3A%20%7B%2053CAAF91%20%7D%20and%20content%3A%20%7B%201AC64679%20%7D%20and%20content%3A%20%7B%20A06A3DD8%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`ror13AddHash32Sub20h`
  - `CreateRemoteThread`: 0x11A0EB1
  - `VirtualAlloc`: 0x302EBE1C
  - `VirtualProtect`: 0x1803B7E3
  - `WriteProcessMemory`: 0x6659DE75
  - `(content: { B10E1A01 } and content: { 1CBE2E30 } and content: { E3B70318 } and content: { 75DE5966 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20B10E1A01%20%7D%20and%20content%3A%20%7B%201CBE2E30%20%7D%20and%20content%3A%20%7B%20E3B70318%20%7D%20and%20content%3A%20%7B%2075DE5966%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`ror13AddWithNullHash32`
  - `CreateRemoteThread`: 0xE6EB95EC
  - `VirtualAlloc`: 0x52A48D7E
  - `VirtualProtect`: 0x30DBCA36
  - `WriteProcessMemory`: 0x550EC1EB
  - `(content: { EC95EBE6 } and content: { 7E8DA452 } and content: { 36CADB30 } and content: { EBC10E55 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20EC95EBE6%20%7D%20and%20content%3A%20%7B%207E8DA452%20%7D%20and%20content%3A%20%7B%2036CADB30%20%7D%20and%20content%3A%20%7B%20EBC10E55%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 4

`ror7AddHash32`
  - `CreateRemoteThread`: 0x669AEB63
  - `VirtualAlloc`: 0x1EDE5967
  - `VirtualProtect`: 0xEF64A41E
  - `WriteProcessMemory`: 0x97410F58
  - `(content: { 63EB9A66 } and content: { 6759DE1E } and content: { 1EA464EF } and content: { 580F4197 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%2063EB9A66%20%7D%20and%20content%3A%20%7B%206759DE1E%20%7D%20and%20content%3A%20%7B%201EA464EF%20%7D%20and%20content%3A%20%7B%20580F4197%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 2

`ror9AddHash32`
  - `CreateRemoteThread`: 0x33373FE2
  - `VirtualAlloc`: 0x7F35AD1C
  - `VirtualProtect`: 0xCCF7DCE1
  - `WriteProcessMemory`: 0x82C8C25
  - `(content: { E23F3733 } and content: { 1CAD357F } and content: { E1DCF7CC } and content: { 258C2C08 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20E23F3733%20%7D%20and%20content%3A%20%7B%201CAD357F%20%7D%20and%20content%3A%20%7B%20E1DCF7CC%20%7D%20and%20content%3A%20%7B%20258C2C08%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`shift0x82F63B78`
  - `CreateRemoteThread`: 0xB43B0471
  - `VirtualAlloc`: 0x4B3E79CB
  - `VirtualProtect`: 0x17CCE3F6
  - `WriteProcessMemory`: 0xEE10B992
  - `(content: { 71043BB4 } and content: { CB793E4B } and content: { F6E3CC17 } and content: { 92B910EE }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%2071043BB4%20%7D%20and%20content%3A%20%7B%20CB793E4B%20%7D%20and%20content%3A%20%7B%20F6E3CC17%20%7D%20and%20content%3A%20%7B%2092B910EE%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`shl7Shr19AddHash32`
  - `CreateRemoteThread`: 0x46902C89
  - `VirtualAlloc`: 0x929199C0
  - `VirtualProtect`: 0x971112C8
  - `WriteProcessMemory`: 0x9CA4F7AC
  - `(content: { 892C9046 } and content: { C0999192 } and content: { C8121197 } and content: { ACF7A49C }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20892C9046%20%7D%20and%20content%3A%20%7B%20C0999192%20%7D%20and%20content%3A%20%7B%20C8121197%20%7D%20and%20content%3A%20%7B%20ACF7A49C%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`shl7Shr19XorHash32`
  - `CreateRemoteThread`: 0x98E58F45
  - `VirtualAlloc`: 0xC2327ADF
  - `VirtualProtect`: 0xADD67F7C
  - `WriteProcessMemory`: 0xC05D44C3
  - `(content: { 458FE598 } and content: { DF7A32C2 } and content: { 7C7FD6AD } and content: { C3445DC0 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20458FE598%20%7D%20and%20content%3A%20%7B%20DF7A32C2%20%7D%20and%20content%3A%20%7B%207C7FD6AD%20%7D%20and%20content%3A%20%7B%20C3445DC0%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`shl7SubHash32DoublePulser`
  - `CreateRemoteThread`: 0xD5A771D4
  - `VirtualAlloc`: 0x293836
  - `VirtualProtect`: 0x88FD7C1C
  - `WriteProcessMemory`: 0xFDCF5DCF
  - `(content: { D471A7D5 } and content: { 36382900 } and content: { 1C7CFD88 } and content: { CF5DCFFD }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20D471A7D5%20%7D%20and%20content%3A%20%7B%2036382900%20%7D%20and%20content%3A%20%7B%201C7CFD88%20%7D%20and%20content%3A%20%7B%20CF5DCFFD%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`shr2Shl5XorHash32`
  - `CreateRemoteThread`: 0x7E8CC469
  - `VirtualAlloc`: 0x8ABF0222
  - `VirtualProtect`: 0xBD9C0637
  - `WriteProcessMemory`: 0xD51E7B84
  - `(content: { 69C48C7E } and content: { 2202BF8A } and content: { 37069CBD } and content: { 847B1ED5 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%2069C48C7E%20%7D%20and%20content%3A%20%7B%202202BF8A%20%7D%20and%20content%3A%20%7B%2037069CBD%20%7D%20and%20content%3A%20%7B%20847B1ED5%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`sll1AddHash32`
  - `CreateRemoteThread`: 0x33CD714
  - `VirtualAlloc`: 0xE3142
  - `VirtualProtect`: 0x38D13C
  - `WriteProcessMemory`: 0x3980F62
  - `(content: { 14D73C03 } and content: { 42310E00 } and content: { 3CD13800 } and content: { 620F9803 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%2014D73C03%20%7D%20and%20content%3A%20%7B%2042310E00%20%7D%20and%20content%3A%20%7B%203CD13800%20%7D%20and%20content%3A%20%7B%20620F9803%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 2

`xorRol9Hash32`
  - `CreateRemoteThread`: 0xE097A9A9
  - `VirtualAlloc`: 0x3259F6BA
  - `VirtualProtect`: 0x6CE440DF
  - `WriteProcessMemory`: 0xC8203FD6
  - `(content: { A9A997E0 } and content: { BAF65932 } and content: { DF40E46C } and content: { D63F20C8 }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20A9A997E0%20%7D%20and%20content%3A%20%7B%20BAF65932%20%7D%20and%20content%3A%20%7B%20DF40E46C%20%7D%20and%20content%3A%20%7B%20D63F20C8%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

`xorShr8Hash32`
  - `CreateRemoteThread`: 0xDA1191B7
  - `VirtualAlloc`: 0x7EA7543F
  - `VirtualProtect`: 0xD03A6856
  - `WriteProcessMemory`: 0x5BB09A4F
  - `(content: { B79111DA } and content: { 3F54A77E } and content: { 56683AD0 } and content: { 4F9AB05B }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%20B79111DA%20%7D%20and%20content%3A%20%7B%203F54A77E%20%7D%20and%20content%3A%20%7B%2056683AD0%20%7D%20and%20content%3A%20%7B%204F9AB05B%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 0

