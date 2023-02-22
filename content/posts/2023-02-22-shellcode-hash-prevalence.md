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

```
   9162* sll1AddHash32 (many FPs due to hash collisions)
    391  ror13AddHash32
     95  crc32
     75  ror13AddHash32AddDll
     59  rol5XorHash32
     27  poisonIvyHash
     23  shr2Shl5XorHash32
     16  rol7XorHash32
     16  imul83hAdd
     13  or21hXorRor11Hash32
     12  fnv1Xor67f
      9  xorShr8Hash32
      7  ror9AddHash32
      7  ror13AddHash32Sub20h
      5  ror13AddWithNullHash32
      5  crc32Xor0xca9d4d4e
      5  addRor4WithNullHash32
      5  addRor13Hash32
      5  addRol5HashOncemore32
      5  add1505Shl5Hash32
      4  shl7Shr19AddHash32
      4  ror7AddHash32
      4  rol7AddHash32
      4  chAddRol8Hash32
      3  xorRol9Hash32
      3  ror13AddHash32Sub1
      3  ror11AddHash32
      3  rol9XorHash32
      3  rol9AddHash32
      3  rol3XorHash32
      3  playWith0xe8677835Hash
      3  hash_Carbanak
      2  rol3XorEax
      2  mult21AddHash32
      2  imul21hAddHash32
      2  addRor13HashOncemore32
      1  shl7SubHash32DoublePulser
      1  shift0x82F63B78
      1  ror13AddHash32DllSimple
      1  rol8Xor0xB0D4D06Hash32
      1  rol7AddXor2Hash32
      1  rol5AddHash32
      1  hash_ror13AddUpperDllnameHash32
      1  dualaccModFFF1Hash
      1  crc32bzip2lower
      1  adler32_666
```

Using the [flare-ida](https://github.com/mandiant/flare-ida) [shellcode hashes database](https://github.com/mandiant/flare-ida/tree/master/shellcode_hashes) `sc_hashes.db`, we can generate VirusTotal queries to search for PE files with interesting hashes like this:

`add1505Shl5Hash32`
  - `CreateRemoteThread`: 0xAA30775D
  - `VirtualAlloc`: 0x382C0F97
  - `VirtualProtect`: 0x844FF18D
  - `WriteProcessMemory`: 0x6F22E8C8
  - `(content: { 5D7730AA } and content: { 970F2C38 } and content: { 8DF14F84 } and content: { C8E8226F }) and size:100kb- and (tag:pedll or tag:peexe)`
  - [search](https://www.virustotal.com/gui/search/%28content%3A%20%7B%205D7730AA%20%7D%20and%20content%3A%20%7B%20970F2C38%20%7D%20and%20content%3A%20%7B%208DF14F84%20%7D%20and%20content%3A%20%7B%20C8E8226F%20%7D%29%20and%20size%3A100kb-%20and%20%28tag%3Apedll%20or%20tag%3Apeexe%29/files)
  - count: 1

And the key results look like this:

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


<details>
<summary>Python code to generate VT queries</summary>

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

</details>

<details>
<summary>complete VT search results</summary>

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
  - `VirtualAlloc`: 0xE3142 (note: only 20 bits used here)
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

</details>

We can also generate yara rules for a retrohunt that match a collection of hashes. These rules benefit from the `3 or more` clauses that are a bit more flexible then requiring *all* hash values to be present:

```yara
rule sc_hash_add1505Shl5Hash32
{
    meta:
        description = "search for shellcode hash add1505Shl5Hash32"

    strings:
        $CreateRemoteThread = { 5D7730AA }
        $GetProcAddress = { 1FBB31CF }
        $GetVersion = { 8B618227 }
        $InternetOpenA = { A170ADF4 }
        $InternetOpenW = { B770ADF4 }
        $LoadLibraryA = { FBF0BF5F }
        $LoadLibraryW = { 11F1BF5F }
        $Sleep = { FEE5190E }
        $VirtualAlloc = { 970F2C38 }
        $VirtualProtect = { 8DF14F84 }
        $WSAStartup = { 83C62861 }
        $WriteProcessMemory = { C8E8226F }
        $socket = { 2E03311C }

    condition:
        filesize < 500KB and 3 of them
}
```

<details>
<summary>Python code to generate yara rules</summary>

```py
import urllib
import sqlite3
import binascii
import textwrap
import collections

db = sqlite3.connect("./shellcode_hashes/sc_hashes.db")
conn = db.cursor()
cursor = conn.execute('''
  SELECT symbol_name, hash_name, hash_size, hash_val 
  FROM symbol_hashes
  INNER JOIN hash_types ON symbol_hashes.hash_type = hash_types.hash_type
  WHERE symbol_name IN (
    "LoadLibraryA", 
    "LoadLibraryW", 
    "GetProcAddress", 
    "VirtualAlloc", 
    "VirtualProtect", 
    "CreateRemoteThread", 
    "WriteProcessMemory",
    "socket",
    "InternetOpenA",
    "InternetOpenW",
    "GetVersion",
    "WSAStartup",
    "Sleep"
  )
  ORDER BY symbol_name, hash_name;
''')

hashes = collections.defaultdict(dict)
for symbol_name, hash_name, hash_size, hash_val in cursor.fetchall():
    assert hash_size == 32
    hashes[hash_name][symbol_name] = hash_val
    
for hash_name, symbols in sorted(hashes.items()):
    strings = []
    for symbol_name, hash_val in sorted(symbols.items()):
        content = binascii.hexlify(hash_val.to_bytes(4, "little")).decode("ascii").upper()
        strings.append(f'${symbol_name} = {{ {content} }}')
        
    rule = """
rule sc_hash_{hash_name}
{{
    meta:
        description = "search for shellcode hash {hash_name}"

    strings:
{strings}

    condition:
        filesize < 500KB and 3 of them
}}
        """.format(hash_name=hash_name, strings="\n".join(strings))
    
    # re-align the strings section
    rule = rule.replace("$", "        $")
        
    print(rule)
```
</details>

<details>
<summary>complete yara rule listing</summary>

```yara
rule sc_hash_add1505Shl5Hash32
{
    meta:
        description = "search for shellcode hash add1505Shl5Hash32"

    strings:
        $CreateRemoteThread = { 5D7730AA }
        $GetProcAddress = { 1FBB31CF }
        $GetVersion = { 8B618227 }
        $InternetOpenA = { A170ADF4 }
        $InternetOpenW = { B770ADF4 }
        $LoadLibraryA = { FBF0BF5F }
        $LoadLibraryW = { 11F1BF5F }
        $Sleep = { FEE5190E }
        $VirtualAlloc = { 970F2C38 }
        $VirtualProtect = { 8DF14F84 }
        $WSAStartup = { 83C62861 }
        $WriteProcessMemory = { C8E8226F }
        $socket = { 2E03311C }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_addRol5HashOncemore32
{
    meta:
        description = "search for shellcode hash addRol5HashOncemore32"

    strings:
        $CreateRemoteThread = { C8B1D1C7 }
        $GetProcAddress = { 67425625 }
        $GetVersion = { 4511EC91 }
        $InternetOpenA = { D83FDE1A }
        $InternetOpenW = { D897DE1A }
        $LoadLibraryA = { CC70776B }
        $LoadLibraryW = { CCC8776B }
        $Sleep = { 1540849E }
        $VirtualAlloc = { 2311D8E9 }
        $VirtualProtect = { D8EE972A }
        $WSAStartup = { B9B65058 }
        $WriteProcessMemory = { 9AF6E499 }
        $socket = { B453E48C }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_addRor13Hash32
{
    meta:
        description = "search for shellcode hash addRor13Hash32"

    strings:
        $CreateRemoteThread = { EC95EBE6 }
        $GetProcAddress = { 6FE053E5 }
        $GetVersion = { CC7E0E0B }
        $InternetOpenA = { 42BF4A21 }
        $InternetOpenW = { 42BFFA21 }
        $LoadLibraryA = { 72607774 }
        $LoadLibraryW = { 72602775 }
        $Sleep = { 6AD9864D }
        $VirtualAlloc = { 7E8DA452 }
        $VirtualProtect = { 36CADB30 }
        $WSAStartup = { E7DF596E }
        $WriteProcessMemory = { EBC10E55 }
        $socket = { 7849725B }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_addRor13HashOncemore32
{
    meta:
        description = "search for shellcode hash addRor13HashOncemore32"

    strings:
        $CreateRemoteThread = { 5C3767AF }
        $GetProcAddress = { 9F2A7F03 }
        $GetVersion = { 735860F6 }
        $InternetOpenA = { 550A11FA }
        $InternetOpenW = { D50F11FA }
        $LoadLibraryA = { BBA39303 }
        $LoadLibraryW = { 3BA99303 }
        $Sleep = { 366C52CB }
        $VirtualAlloc = { 2495F26B }
        $VirtualProtect = { DE86B151 }
        $WSAStartup = { CE723BFF }
        $WriteProcessMemory = { 76A85A0F }
        $socket = { 92DBC24B }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_addRor4WithNullHash32
{
    meta:
        description = "search for shellcode hash addRor4WithNullHash32"

    strings:
        $CreateRemoteThread = { 5309D7D6 }
        $GetProcAddress = { F7331321 }
        $GetVersion = { ADA8D00E }
        $InternetOpenA = { AC6F07A0 }
        $InternetOpenW = { AC6F07B6 }
        $LoadLibraryA = { 8E488B63 }
        $LoadLibraryW = { 8E488B79 }
        $Sleep = { 0013BC76 }
        $VirtualAlloc = { 2868E125 }
        $VirtualProtect = { D73458A2 }
        $WSAStartup = { 97883BD0 }
        $WriteProcessMemory = { 05B0AC23 }
        $socket = { 30A6C17A }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_adler32_666
{
    meta:
        description = "search for shellcode hash adler32_666"

    strings:
        $CreateRemoteThread = { D2078C60 }
        $GetProcAddress = { B4060543 }
        $GetVersion = { A0057C2A }
        $InternetOpenA = { 7606213D }
        $InternetOpenW = { 8C06373D }
        $LoadLibraryA = { 10068D35 }
        $LoadLibraryW = { 2606A335 }
        $Sleep = { 13047A11 }
        $VirtualAlloc = { 2C06FC36 }
        $VirtualProtect = { E206E444 }
        $WSAStartup = { B8051D2B }
        $WriteProcessMemory = { 1D082063 }
        $socket = { 6304E415 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_chAddRol8Hash32
{
    meta:
        description = "search for shellcode hash chAddRol8Hash32"

    strings:
        $CreateRemoteThread = { 6012764D }
        $GetProcAddress = { 11783228 }
        $GetVersion = { 3E571C4D }
        $InternetOpenA = { 5146335E }
        $InternetOpenW = { 5146255E }
        $LoadLibraryA = { 415F5935 }
        $LoadLibraryW = { 415F4F35 }
        $Sleep = { 5A3F2365 }
        $VirtualAlloc = { 436B7E0A }
        $VirtualProtect = { 375E3B07 }
        $WSAStartup = { 05672040 }
        $WriteProcessMemory = { 673A7972 }
        $socket = { 147F6816 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_crc32
{
    meta:
        description = "search for shellcode hash crc32"

    strings:
        $CreateRemoteThread = { 108C80FF }
        $GetProcAddress = { FF1F7CC9 }
        $GetVersion = { 0F1ACF4C }
        $InternetOpenA = { 3DA816DA }
        $InternetOpenW = { 6C1DC22E }
        $LoadLibraryA = { 8DBDC13F }
        $LoadLibraryW = { DC0815CB }
        $Sleep = { A8EDF2CE }
        $VirtualAlloc = { 4A0DCE09 }
        $VirtualProtect = { 2F6F0610 }
        $WSAStartup = { 93FCF5A0 }
        $WriteProcessMemory = { 2E97584F }
        $socket = { BB68E505 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_crc32Xor0xca9d4d4e
{
    meta:
        description = "search for shellcode hash crc32Xor0xca9d4d4e"

    strings:
        $CreateRemoteThread = { 5EC11D35 }
        $GetProcAddress = { B152E103 }
        $GetVersion = { 41575286 }
        $InternetOpenA = { 73E58B10 }
        $InternetOpenW = { 22505FE4 }
        $LoadLibraryA = { C3F05CF5 }
        $LoadLibraryW = { 92458801 }
        $Sleep = { E6A06F04 }
        $VirtualAlloc = { 044053C3 }
        $VirtualProtect = { 61229BDA }
        $WSAStartup = { DDB1686A }
        $WriteProcessMemory = { 60DAC585 }
        $socket = { F52578CF }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_crc32bzip2lower
{
    meta:
        description = "search for shellcode hash crc32bzip2lower"

    strings:
        $CreateRemoteThread = { A06C72DC }
        $GetProcAddress = { 28F4DF5C }
        $GetVersion = { A3ED4E26 }
        $InternetOpenA = { 47AE9414 }
        $InternetOpenW = { 85380342 }
        $LoadLibraryA = { CA082543 }
        $LoadLibraryW = { 089EB215 }
        $Sleep = { E1EA8806 }
        $VirtualAlloc = { 3CE91D9A }
        $VirtualProtect = { 0D63E81E }
        $WSAStartup = { 746F3CA8 }
        $WriteProcessMemory = { 8167E170 }
        $socket = { C5BFA946 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_dualaccModFFF1Hash
{
    meta:
        description = "search for shellcode hash dualaccModFFF1Hash"

    strings:
        $CreateRemoteThread = { 1907AA42 }
        $GetProcAddress = { 7B05C727 }
        $GetVersion = { 07044215 }
        $InternetOpenA = { 1D055C24 }
        $InternetOpenW = { 33057224 }
        $LoadLibraryA = { 9704811D }
        $LoadLibraryW = { AD04971D }
        $Sleep = { FA01BD05 }
        $VirtualAlloc = { D304701F }
        $VirtualProtect = { C905062B }
        $WSAStartup = { DF03C313 }
        $WriteProcessMemory = { 64071E45 }
        $socket = { 8A02EE08 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_fnv1Xor67f
{
    meta:
        description = "search for shellcode hash fnv1Xor67f"

    strings:
        $CreateRemoteThread = { 1CC298C3 }
        $GetProcAddress = { 5A51F4F8 }
        $GetVersion = { E6512F3A }
        $InternetOpenA = { 98903BE2 }
        $InternetOpenW = { EE7C3BD0 }
        $LoadLibraryA = { 7001B253 }
        $LoadLibraryW = { C6ECB141 }
        $Sleep = { D72AA62F }
        $VirtualAlloc = { 7E532803 }
        $VirtualProtect = { 8C270682 }
        $WSAStartup = { 205A1220 }
        $WriteProcessMemory = { 958808C0 }
        $socket = { 13701290 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_hash_Carbanak
{
    meta:
        description = "search for shellcode hash hash_Carbanak"

    strings:
        $CreateRemoteThread = { 74158B04 }
        $GetProcAddress = { 031D3C0B }
        $GetVersion = { CE44CD0C }
        $InternetOpenA = { 31A3EC0C }
        $InternetOpenW = { 27A3EC0C }
        $LoadLibraryA = { F1F0AD0A }
        $LoadLibraryW = { C7F0AD0A }
        $Sleep = { C02B5A00 }
        $VirtualAlloc = { E3CAD803 }
        $VirtualProtect = { 64182D07 }
        $WSAStartup = { A05CAD0A }
        $WriteProcessMemory = { 99B04806 }
        $socket = { C4A1A507 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_hash_ror13AddUpperDllnameHash32
{
    meta:
        description = "search for shellcode hash hash_ror13AddUpperDllnameHash32"

    strings:
        $CreateRemoteThread = { F466E9E0 }
        $GetProcAddress = { C1C639EA }
        $GetVersion = { 784B053E }
        $InternetOpenA = { CDE68745 }
        $InternetOpenW = { E3E68745 }
        $LoadLibraryA = { A5183A5A }
        $LoadLibraryW = { BB183A5A }
        $Sleep = { C7135949 }
        $VirtualAlloc = { 6B94DBFF }
        $VirtualProtect = { 329072E7 }
        $WSAStartup = { A6BF8E2A }
        $WriteProcessMemory = { B8346946 }
        $socket = { 49DDC037 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_imul21hAddHash32
{
    meta:
        description = "search for shellcode hash imul21hAddHash32"

    strings:
        $CreateRemoteThread = { 7D152B25 }
        $GetProcAddress = { BFC1CFDE }
        $GetVersion = { 8B68BFC2 }
        $InternetOpenA = { 617791A7 }
        $InternetOpenW = { 777791A7 }
        $LoadLibraryA = { DB2F07B7 }
        $LoadLibraryW = { F12F07B7 }
        $Sleep = { 7ECD070E }
        $VirtualAlloc = { 57C27B09 }
        $VirtualProtect = { 0D5057E8 }
        $WSAStartup = { C3892E14 }
        $WriteProcessMemory = { E80A93B7 }
        $socket = { 6EC636CF }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_imul83hAdd
{
    meta:
        description = "search for shellcode hash imul83hAdd"

    strings:
        $CreateRemoteThread = { 9C9C4671 }
        $GetProcAddress = { 54B8B99A }
        $GetVersion = { DA23448E }
        $InternetOpenA = { 42B6C408 }
        $InternetOpenW = { 58B6C408 }
        $LoadLibraryA = { 781F207F }
        $LoadLibraryW = { 8E1F207F }
        $Sleep = { 538085BF }
        $VirtualAlloc = { 623489DE }
        $VirtualProtect = { 04C46E6C }
        $WSAStartup = { 342652B3 }
        $WriteProcessMemory = { 85EA1BA1 }
        $socket = { 9F2D40A6 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_mult21AddHash32
{
    meta:
        description = "search for shellcode hash mult21AddHash32"

    strings:
        $CreateRemoteThread = { 1823894B }
        $GetProcAddress = { 5AC1CBC2 }
        $GetVersion = { 4682D4F1 }
        $InternetOpenA = { 7C1BB287 }
        $InternetOpenW = { 921BB287 }
        $LoadLibraryA = { 762C1D07 }
        $LoadLibraryW = { 8C2C1D07 }
        $Sleep = { D9E51A06 }
        $VirtualAlloc = { 124B89DF }
        $VirtualProtect = { C8F7E977 }
        $WSAStartup = { 3EE77A2B }
        $WriteProcessMemory = { 83947B10 }
        $socket = { 69FE5114 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_or21hXorRor11Hash32
{
    meta:
        description = "search for shellcode hash or21hXorRor11Hash32"

    strings:
        $CreateRemoteThread = { B46984DF }
        $GetProcAddress = { 77CD6633 }
        $GetVersion = { 6E6A5357 }
        $InternetOpenA = { 767C65A9 }
        $InternetOpenW = { 76CC65A9 }
        $LoadLibraryA = { 927CD094 }
        $LoadLibraryW = { 92CCD094 }
        $Sleep = { CA58C520 }
        $VirtualAlloc = { B62D558C }
        $VirtualProtect = { 3F1D6374 }
        $WSAStartup = { A61AD74C }
        $WriteProcessMemory = { 102E028F }
        $socket = { 1A99C52E }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_or23hXorRor17Hash32
{
    meta:
        description = "search for shellcode hash or23hXorRor17Hash32"

    strings:
        $CreateRemoteThread = { A420E6BA }
        $GetProcAddress = { 3300A198 }
        $GetVersion = { 4CF467F8 }
        $InternetOpenA = { 42189903 }
        $InternetOpenW = { 4218B103 }
        $LoadLibraryA = { 1F0CB98E }
        $LoadLibraryW = { 1F0C918E }
        $Sleep = { 6C07BE0D }
        $VirtualAlloc = { 8FD75888 }
        $VirtualProtect = { 3259AD29 }
        $WSAStartup = { 2CA4BFD0 }
        $WriteProcessMemory = { 2C134661 }
        $socket = { 6C1B560E }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_playWith0xe8677835Hash
{
    meta:
        description = "search for shellcode hash playWith0xe8677835Hash"

    strings:
        $CreateRemoteThread = { 232763D4 }
        $GetProcAddress = { 54EF20A1 }
        $GetVersion = { 23CFB093 }
        $InternetOpenA = { F7BD34F1 }
        $InternetOpenW = { 26D506F4 }
        $LoadLibraryA = { D118ACA7 }
        $LoadLibraryW = { 00709EA2 }
        $Sleep = { 1AE4C3E4 }
        $VirtualAlloc = { F1FD63E7 }
        $VirtualProtect = { 5F901FB4 }
        $WSAStartup = { 0AE6AFC2 }
        $WriteProcessMemory = { BF8A12B2 }
        $socket = { E9DAC1F4 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_poisonIvyHash
{
    meta:
        description = "search for shellcode hash poisonIvyHash"

    strings:
        $CreateRemoteThread = { 657F4ACF }
        $GetProcAddress = { 1F7CC9FF }
        $GetVersion = { 063DF142 }
        $InternetOpenA = { 34B5B08A }
        $InternetOpenW = { E3002896 }
        $LoadLibraryA = { ADD13441 }
        $LoadLibraryW = { 7A64AC5D }
        $Sleep = { BA36C10A }
        $VirtualAlloc = { 0E890244 }
        $VirtualProtect = { BBD4C379 }
        $WSAStartup = { 8FD8A4BB }
        $WriteProcessMemory = { D5BA9B0E }
        $socket = { E160B48E }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol3XorEax
{
    meta:
        description = "search for shellcode hash rol3XorEax"

    strings:
        $CreateRemoteThread = { E2F9A7DB }
        $GetProcAddress = { 08EE319C }
        $GetVersion = { 415790C0 }
        $InternetOpenA = { 74969982 }
        $InternetOpenW = { C4969982 }
        $LoadLibraryA = { FB328CAE }
        $LoadLibraryW = { 4B328CAE }
        $Sleep = { A0EAF51B }
        $VirtualAlloc = { DEC3E3FF }
        $VirtualProtect = { EBA99CA9 }
        $WSAStartup = { 05945D86 }
        $WriteProcessMemory = { 660643EF }
        $socket = { 2207CA13 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol3XorHash32
{
    meta:
        description = "search for shellcode hash rol3XorHash32"

    strings:
        $CreateRemoteThread = { C2665F4A }
        $GetProcAddress = { 849B50F2 }
        $GetVersion = { 545FED52 }
        $InternetOpenA = { 230E6A56 }
        $InternetOpenW = { 350E6A56 }
        $LoadLibraryA = { 89FD12A4 }
        $LoadLibraryW = { 9FFD12A4 }
        $Sleep = { 18F20500 }
        $VirtualAlloc = { AED016AB }
        $VirtualProtect = { 462FFFC5 }
        $WSAStartup = { DAEA50E2 }
        $WriteProcessMemory = { 55D54AB0 }
        $socket = { 9CAF3F00 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol5AddHash32
{
    meta:
        description = "search for shellcode hash rol5AddHash32"

    strings:
        $CreateRemoteThread = { 6CF43172 }
        $GetProcAddress = { 9055C999 }
        $GetVersion = { 047B6451 }
        $InternetOpenA = { 8FB706F6 }
        $InternetOpenW = { A5B706F6 }
        $LoadLibraryA = { DCDD1A33 }
        $LoadLibraryW = { F2DD1A33 }
        $Sleep = { 10A16705 }
        $VirtualAlloc = { 0476FA48 }
        $VirtualProtect = { FBA50AB6 }
        $WSAStartup = { 2D1456AE }
        $WriteProcessMemory = { 3D79A6A6 }
        $socket = { 143923ED }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol5XorHash32
{
    meta:
        description = "search for shellcode hash rol5XorHash32"

    strings:
        $CreateRemoteThread = { 536430CA }
        $GetProcAddress = { DBB6B6E5 }
        $GetVersion = { 33AF144D }
        $InternetOpenA = { CE481508 }
        $InternetOpenW = { D8481508 }
        $LoadLibraryA = { 3B00A1B4 }
        $LoadLibraryW = { 2D00A1B4 }
        $Sleep = { D0980707 }
        $VirtualAlloc = { 338A8DA4 }
        $VirtualProtect = { 825A154A }
        $WSAStartup = { C44E262E }
        $WriteProcessMemory = { 7061462A }
        $socket = { D420C0E0 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol7AddHash32
{
    meta:
        description = "search for shellcode hash rol7AddHash32"

    strings:
        $CreateRemoteThread = { 892C9046 }
        $GetProcAddress = { 54157FFC }
        $GetVersion = { 41D36314 }
        $InternetOpenA = { 18EC94F5 }
        $InternetOpenW = { 2EEC94F5 }
        $LoadLibraryA = { C9FFDF10 }
        $LoadLibraryW = { DFFFDF10 }
        $Sleep = { F572993D }
        $VirtualAlloc = { C0999192 }
        $VirtualProtect = { C8121197 }
        $WSAStartup = { C18AE0F1 }
        $WriteProcessMemory = { ACF7A49C }
        $socket = { 92F67AFC }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol7AddXor2Hash32
{
    meta:
        description = "search for shellcode hash rol7AddXor2Hash32"

    strings:
        $CreateRemoteThread = { 247A7273 }
        $GetProcAddress = { E2DC5B0A }
        $GetVersion = { 4D4A28F6 }
        $InternetOpenA = { AB33F1D3 }
        $InternetOpenW = { BD33F1D3 }
        $LoadLibraryA = { 3BC823F3 }
        $LoadLibraryW = { 4DC823F3 }
        $Sleep = { F7F3D91D }
        $VirtualAlloc = { 4DE1D5B4 }
        $VirtualProtect = { 3B5A7569 }
        $WSAStartup = { D303A50F }
        $WriteProcessMemory = { 4532FECD }
        $socket = { 84773ADC }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol7XorHash32
{
    meta:
        description = "search for shellcode hash rol7XorHash32"

    strings:
        $CreateRemoteThread = { B37418E6 }
        $GetProcAddress = { EEEAC01F }
        $GetVersion = { E22C93CB }
        $InternetOpenA = { D73D5908 }
        $InternetOpenW = { C13D5908 }
        $LoadLibraryA = { 2680ACC8 }
        $LoadLibraryW = { 3080ACC8 }
        $Sleep = { F572993D }
        $VirtualAlloc = { FE6A7A69 }
        $VirtualProtect = { 5A6FDEA9 }
        $WSAStartup = { 7D75DECD }
        $WriteProcessMemory = { 35BFA0BE }
        $socket = { 6AF17AFC }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol8Xor0xB0D4D06Hash32
{
    meta:
        description = "search for shellcode hash rol8Xor0xB0D4D06Hash32"

    strings:
        $CreateRemoteThread = { 41764230 }
        $GetProcAddress = { 8E70D917 }
        $GetVersion = { 78676316 }
        $InternetOpenA = { 71C10B33 }
        $InternetOpenW = { 8BD70B33 }
        $LoadLibraryA = { B663331E }
        $LoadLibraryW = { C075331E }
        $Sleep = { 69850D02 }
        $VirtualAlloc = { 496D1EC6 }
        $VirtualProtect = { 59122F19 }
        $WSAStartup = { 57730A3A }
        $WriteProcessMemory = { 9E66B430 }
        $socket = { 6678D603 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol9AddHash32
{
    meta:
        description = "search for shellcode hash rol9AddHash32"

    strings:
        $CreateRemoteThread = { 4C3DB214 }
        $GetProcAddress = { 892FAC6B }
        $GetVersion = { CBEABFAF }
        $InternetOpenA = { DD66B26B }
        $InternetOpenW = { F366B26B }
        $LoadLibraryA = { EB9FD7E0 }
        $LoadLibraryW = { 01A0D7E0 }
        $Sleep = { A3CF9461 }
        $VirtualAlloc = { 62D9E29E }
        $VirtualProtect = { 2F025491 }
        $WSAStartup = { A4C34D27 }
        $WriteProcessMemory = { 3528647E }
        $socket = { 6731BB19 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_rol9XorHash32
{
    meta:
        description = "search for shellcode hash rol9XorHash32"

    strings:
        $CreateRemoteThread = { D44BF0D4 }
        $GetProcAddress = { A05CDA49 }
        $GetVersion = { 771CA68C }
        $InternetOpenA = { F4B91448 }
        $InternetOpenW = { E2B91448 }
        $LoadLibraryA = { 25D346AF }
        $LoadLibraryW = { 33D346AF }
        $Sleep = { 43CF9461 }
        $VirtualAlloc = { FB2C195D }
        $VirtualProtect = { 2072B66F }
        $WSAStartup = { 433FB005 }
        $WriteProcessMemory = { 1F1064EB }
        $socket = { 87ACA219 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror11AddHash32
{
    meta:
        description = "search for shellcode hash ror11AddHash32"

    strings:
        $CreateRemoteThread = { 6DF53071 }
        $GetProcAddress = { D00589E9 }
        $GetVersion = { C5D3A2F8 }
        $InternetOpenA = { A325F387 }
        $InternetOpenW = { B925F387 }
        $LoadLibraryA = { 97165FFA }
        $LoadLibraryW = { AD165FFA }
        $Sleep = { A694D111 }
        $VirtualAlloc = { BF273F97 }
        $VirtualProtect = { D7122F49 }
        $WSAStartup = { C80BBBB6 }
        $WriteProcessMemory = { C11C2303 }
        $socket = { A5929293 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror13AddHash32
{
    meta:
        description = "search for shellcode hash ror13AddHash32"

    strings:
        $CreateRemoteThread = { DD9CBD72 }
        $GetProcAddress = { AAFC0D7C }
        $GetVersion = { 6181D9CF }
        $InternetOpenA = { 2944E857 }
        $InternetOpenW = { 3F44E857 }
        $LoadLibraryA = { 8E4E0EEC }
        $LoadLibraryW = { A44E0EEC }
        $Sleep = { B0492DDB }
        $VirtualAlloc = { 54CAAF91 }
        $VirtualProtect = { 1BC64679 }
        $WSAStartup = { CBEDFC3B }
        $WriteProcessMemory = { A16A3DD8 }
        $socket = { 6E0B2F49 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror13AddHash32AddDll
{
    meta:
        description = "search for shellcode hash ror13AddHash32AddDll"

    strings:
        $CreateRemoteThread = { C6AC9A79 }
        $GetProcAddress = { 49F70278 }
        $GetVersion = { A695BD9D }
        $InternetOpenA = { 3A5679A7 }
        $InternetOpenW = { 3A5629A8 }
        $LoadLibraryA = { 4C772607 }
        $LoadLibraryW = { 4C77D607 }
        $Sleep = { 44F035E0 }
        $VirtualAlloc = { 58A453E5 }
        $VirtualProtect = { 10E18AC3 }
        $WSAStartup = { AF78498B }
        $WriteProcessMemory = { C5D8BDE7 }
        $socket = { 40E26178 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror13AddHash32DllSimple
{
    meta:
        description = "search for shellcode hash ror13AddHash32DllSimple"

    strings:
        $CreateRemoteThread = { F466E9E0 }
        $GetProcAddress = { C1C639EA }
        $GetVersion = { 784B053E }
        $InternetOpenA = { CDE68745 }
        $InternetOpenW = { E3E68745 }
        $LoadLibraryA = { A5183A5A }
        $LoadLibraryW = { BB183A5A }
        $Sleep = { C7135949 }
        $VirtualAlloc = { 6B94DBFF }
        $VirtualProtect = { 329072E7 }
        $WSAStartup = { A6BF8E2A }
        $WriteProcessMemory = { B8346946 }
        $socket = { 49DDC037 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror13AddHash32Sub1
{
    meta:
        description = "search for shellcode hash ror13AddHash32Sub1"

    strings:
        $CreateRemoteThread = { DC9CBD72 }
        $GetProcAddress = { A9FC0D7C }
        $GetVersion = { 6081D9CF }
        $InternetOpenA = { 2844E857 }
        $InternetOpenW = { 3E44E857 }
        $LoadLibraryA = { 8D4E0EEC }
        $LoadLibraryW = { A34E0EEC }
        $Sleep = { AF492DDB }
        $VirtualAlloc = { 53CAAF91 }
        $VirtualProtect = { 1AC64679 }
        $WSAStartup = { CAEDFC3B }
        $WriteProcessMemory = { A06A3DD8 }
        $socket = { 6D0B2F49 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror13AddHash32Sub20h
{
    meta:
        description = "search for shellcode hash ror13AddHash32Sub20h"

    strings:
        $CreateRemoteThread = { B10E1A01 }
        $GetProcAddress = { 7AEECA1A }
        $GetVersion = { 3175D76E }
        $InternetOpenA = { 103827F6 }
        $InternetOpenW = { 263827F6 }
        $LoadLibraryA = { 76468B8A }
        $LoadLibraryW = { 8C468B8A }
        $Sleep = { 90412D9A }
        $VirtualAlloc = { 1CBE2E30 }
        $VirtualProtect = { E3B70318 }
        $WSAStartup = { 9AE5FAFA }
        $WriteProcessMemory = { 75DE5966 }
        $socket = { 3E032D08 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror13AddWithNullHash32
{
    meta:
        description = "search for shellcode hash ror13AddWithNullHash32"

    strings:
        $CreateRemoteThread = { EC95EBE6 }
        $GetProcAddress = { 6FE053E5 }
        $GetVersion = { CC7E0E0B }
        $InternetOpenA = { 42BF4A21 }
        $InternetOpenW = { 42BFFA21 }
        $LoadLibraryA = { 72607774 }
        $LoadLibraryW = { 72602775 }
        $Sleep = { 6AD9864D }
        $VirtualAlloc = { 7E8DA452 }
        $VirtualProtect = { 36CADB30 }
        $WSAStartup = { E7DF596E }
        $WriteProcessMemory = { EBC10E55 }
        $socket = { 7849725B }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror7AddHash32
{
    meta:
        description = "search for shellcode hash ror7AddHash32"

    strings:
        $CreateRemoteThread = { 63EB9A66 }
        $GetProcAddress = { 85DFAFBB }
        $GetVersion = { 29056295 }
        $InternetOpenA = { 0C88834A }
        $InternetOpenW = { 2288834A }
        $LoadLibraryA = { 3274910C }
        $LoadLibraryW = { 4874910C }
        $Sleep = { A06597CB }
        $VirtualAlloc = { 6759DE1E }
        $VirtualProtect = { 1EA464EF }
        $WSAStartup = { 3D6AB480 }
        $WriteProcessMemory = { 580F4197 }
        $socket = { 731FAF2B }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_ror9AddHash32
{
    meta:
        description = "search for shellcode hash ror9AddHash32"

    strings:
        $CreateRemoteThread = { E23F3733 }
        $GetProcAddress = { 8E9F4572 }
        $GetVersion = { BD27E7BF }
        $InternetOpenA = { 30807D61 }
        $InternetOpenW = { 46807D61 }
        $LoadLibraryA = { CACCDE43 }
        $LoadLibraryW = { E0CCDE43 }
        $Sleep = { F54D9962 }
        $VirtualAlloc = { 1CAD357F }
        $VirtualProtect = { E1DCF7CC }
        $WSAStartup = { 38DB69A1 }
        $WriteProcessMemory = { 258C2C08 }
        $socket = { DBCC3226 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_shift0x82F63B78
{
    meta:
        description = "search for shellcode hash shift0x82F63B78"

    strings:
        $CreateRemoteThread = { 71043BB4 }
        $GetProcAddress = { F5F8EA17 }
        $GetVersion = { BEFA8EB6 }
        $InternetOpenA = { 574290D6 }
        $InternetOpenW = { D0626FE0 }
        $LoadLibraryA = { A6844C12 }
        $LoadLibraryW = { 21A4B324 }
        $Sleep = { 12D29FAB }
        $VirtualAlloc = { CB793E4B }
        $VirtualProtect = { F6E3CC17 }
        $WSAStartup = { C4976C23 }
        $WriteProcessMemory = { 92B910EE }
        $socket = { 8334E1BF }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_shl7Shr19AddHash32
{
    meta:
        description = "search for shellcode hash shl7Shr19AddHash32"

    strings:
        $CreateRemoteThread = { 892C9046 }
        $GetProcAddress = { 54157FFC }
        $GetVersion = { 41D36314 }
        $InternetOpenA = { 18EC94F5 }
        $InternetOpenW = { 2EEC94F5 }
        $LoadLibraryA = { C9FFDF10 }
        $LoadLibraryW = { DFFFDF10 }
        $Sleep = { F572993D }
        $VirtualAlloc = { C0999192 }
        $VirtualProtect = { C8121197 }
        $WSAStartup = { C18AE0F1 }
        $WriteProcessMemory = { ACF7A49C }
        $socket = { 92F67AFC }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_shl7Shr19XorHash32
{
    meta:
        description = "search for shellcode hash shl7Shr19XorHash32"

    strings:
        $CreateRemoteThread = { 458FE598 }
        $GetProcAddress = { C8FAC81B }
        $GetVersion = { C381C560 }
        $InternetOpenA = { F62D51AC }
        $InternetOpenW = { E02D51AC }
        $LoadLibraryA = { 0790E463 }
        $LoadLibraryW = { 1190E463 }
        $Sleep = { 0E082463 }
        $VirtualAlloc = { DF7A32C2 }
        $VirtualProtect = { 7C7FD6AD }
        $WSAStartup = { 5CD88866 }
        $WriteProcessMemory = { C3445DC0 }
        $socket = { 318CC7A2 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_shl7SubHash32DoublePulser
{
    meta:
        description = "search for shellcode hash shl7SubHash32DoublePulser"

    strings:
        $CreateRemoteThread = { D471A7D5 }
        $GetProcAddress = { B8F8FD0A }
        $GetVersion = { FEAD30CF }
        $InternetOpenA = { 8A0990F6 }
        $InternetOpenW = { 741490F6 }
        $LoadLibraryA = { 54BE4801 }
        $LoadLibraryW = { 3EC94801 }
        $Sleep = { A961000E }
        $VirtualAlloc = { 36382900 }
        $VirtualProtect = { 1C7CFD88 }
        $WSAStartup = { 88C48BC1 }
        $WriteProcessMemory = { CF5DCFFD }
        $socket = { EDAB1698 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_shr2Shl5XorHash32
{
    meta:
        description = "search for shellcode hash shr2Shl5XorHash32"

    strings:
        $CreateRemoteThread = { 69C48C7E }
        $GetProcAddress = { AF345093 }
        $GetVersion = { 1A9D12FA }
        $InternetOpenA = { 51E3D63D }
        $InternetOpenW = { 4BE3D63D }
        $LoadLibraryA = { 5B758AF0 }
        $LoadLibraryW = { 65758AF0 }
        $Sleep = { CD110265 }
        $VirtualAlloc = { 2202BF8A }
        $VirtualProtect = { 37069CBD }
        $WSAStartup = { C4141D4B }
        $WriteProcessMemory = { 847B1ED5 }
        $socket = { 677ED77F }

    condition:
        filesize < 500KB and 3 of them
}


rule sc_hash_xorRol9Hash32
{
    meta:
        description = "search for shellcode hash xorRol9Hash32"

    strings:
        $CreateRemoteThread = { A9A997E0 }
        $GetProcAddress = { 9340B9B4 }
        $GetVersion = { 19EF384C }
        $InternetOpenA = { 90E87329 }
        $InternetOpenW = { 90C47329 }
        $LoadLibraryA = { 5E4BA68D }
        $LoadLibraryW = { 5E67A68D }
        $Sleep = { C3869E29 }
        $VirtualAlloc = { BAF65932 }
        $VirtualProtect = { DF40E46C }
        $WSAStartup = { 0B867E60 }
        $WriteProcessMemory = { D63F20C8 }
        $socket = { 330E5945 }

    condition:
        filesize < 500KB and 3 of them
}
        

rule sc_hash_xorShr8Hash32
{
    meta:
        description = "search for shellcode hash xorShr8Hash32"

    strings:
        $CreateRemoteThread = { B79111DA }
        $GetProcAddress = { E552D88D }
        $GetVersion = { 2507D698 }
        $InternetOpenA = { 1908B9E1 }
        $InternetOpenW = { D9601EF4 }
        $LoadLibraryA = { 317EEE06 }
        $LoadLibraryW = { 27A80284 }
        $Sleep = { 3EDDEF6C }
        $VirtualAlloc = { 3F54A77E }
        $VirtualProtect = { 56683AD0 }
        $WSAStartup = { 32885EE7 }
        $WriteProcessMemory = { 4F9AB05B }
        $socket = { 87FDA3FF }

    condition:
        filesize < 500KB and 3 of them
}
```
</details>

Retrohunting across the past 30 days worth of samples yields the following distribution:

```
   9162 sll1AddHash32 (many FPs due to hash collisions)
    391 ror13AddHash32
     95 crc32
     75 ror13AddHash32AddDll
     59 rol5XorHash32
     27 poisonIvyHash
     23 shr2Shl5XorHash32
     16 rol7XorHash32
     16 imul83hAdd
     13 or21hXorRor11Hash32
     12 fnv1Xor67f
      9 xorShr8Hash32
      7 ror9AddHash32
      7 ror13AddHash32Sub20h
      5 ror13AddWithNullHash32
      5 crc32Xor0xca9d4d4e
      5 addRor4WithNullHash32
      5 addRor13Hash32
      5 addRol5HashOncemore32
      5 add1505Shl5Hash32
      4 shl7Shr19AddHash32
      4 ror7AddHash32
      4 rol7AddHash32
      4 chAddRol8Hash32
      3 xorRol9Hash32
      3 ror13AddHash32Sub1
      3 ror11AddHash32
      3 rol9XorHash32
      3 rol9AddHash32
      3 rol3XorHash32
      3 playWith0xe8677835Hash
      3 hash_Carbanak
      2 rol3XorEax
      2 mult21AddHash32
      2 imul21hAddHash32
      2 addRor13HashOncemore32
      1 shl7SubHash32DoublePulser
      1 shift0x82F63B78
      1 ror13AddHash32DllSimple
      1 rol8Xor0xB0D4D06Hash32
      1 rol7AddXor2Hash32
      1 rol5AddHash32
      1 hash_ror13AddUpperDllnameHash32
      1 dualaccModFFF1Hash
      1 crc32bzip2lower
      1 adler32_666
```

The `sll1AddHash32` hashes are surprisingly prevalent. If we peek at some of the matches:

```console
❯ yara sc_hashes.yar tests/data/ -s
...
sc_hash_sll1AddHash32 tests/data//mimikatz.exe_.viv
0x49d373:$GetVersion: 90 49 03 00
0xe10c76:$LoadLibraryA: 86 57 0D 00
0xe10e9c:$LoadLibraryW: B2 57 0D 00
0xd1fc6:$Sleep: BC 1A 00 00
0x11c5b1:$Sleep: BC 1A 00 00
0x1a7527:$Sleep: BC 1A 00 00
0x4e30b0:$WSAStartup: 14 93 03 00
0x1c337b:$socket: A4 36 00 00
...
```

then we see that there are a few values that are "not very random" (only 16-20 bits of information). These are sure to be found in many PE files, in encoded data such as RVAs, etc. So, I think most of these hits can be attributed to false positives.