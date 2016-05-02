---
layout: page
title: "The Microsoft ReFS In-Memory Layout"
date: 2013-01-14 01:02
comments: false
sharing: false
footer: true
---

The refs.sys driver uses the following definitions in memory to manipulate a ReFS file system.

### Structures

#### SmsIndexRoot & SmsIndexBucket

{% highlight c %}

typedef struct _SmsIndexRoot {  // sizeof() == 0x28
    uint32         dwIndexHeaderOffset;
    uint32         padding;
    SmsIndexHeader indexHeader; 
} SmsIndexRoot;

// appears to be the same structure as SmsIndexRoot
typedef struct _SmsIndexBucket {  // sizeof() == 0x28
    uint32   dwIndexHeaderOffset;
    uint32   padding;
    SmsIndexHeader indexHeader; 
} SmsIndexBucket;

{% endhighlight %}    

#### SmsIndexHeader

{% highlight c %}

enum INDEX_IH_FLAGS {
    INDEX_IH_DIRECTOR = 1
};

typedef struct _SmsIndexHeader {  //  sizeof() == 0x20
    uint32   dwFirstIndexEntry;
    uint32   dwNextInsertOffset;
    uint8    bLevel;
    uint8    bFlags;
    uint8[2] padding;
    uint32   dwFirstIndexEntryOffset;
    uint32   dwNumberIndexEntryOffsets;
    uint32   dwEndOfBucketOffset;
    uint32   padding2;
} SmsIndexHeader;

{% endhighlight %}    

#### SmsIndexEntry

{% highlight c %}

enum INDEX_IE_FLAGS {
    INDEX_IE_ENTRY_END  = 2,
    INDEX_IE_ENTRY_DELETED  = 4
};

typedef struct _SmsIndexEntry {  // sizeof() == 0x10
    uint32 dwLength;
    uint16 wKeyOffset;
    uint16 wKeyLength;
    uint16 wFlags;  // see INDEX_IE_FLAGS
    uint16 wDataOffset;
    uint16 wDataLength;
} SmsIndexEntry;

{% endhighlight %}    

#### REFS_NODE_TYPE

ReFS passes about `Node`s that are buffers that begin with a DWORD tag/type that identifies its structure. `REFS_NODE_TYPE` defines the possible tags for  thesestructures.

{% highlight c %}

enum REFS_NODE_TYPE {
    REFS_NTC_VCB             = 0x701,
    REFS_NTC_FCB             = 0x702,
    REFS_NTC_SCB_DATA        = 0x703,      // 0x703-0x705 are not yet ordered
    REFS_NTC_SCB_INDEX       = 0x704,
    REFS_NTC_SCB_ROOT_INDEX  = 0x705,
    REFS_NTC_IRP_CONTEXT     = 0x70A,
    REFS_NTC_LCB             = 0x70B,
    REFS_NTC_BAADFOOD        = 0xBAADF00D,
};

typedef struct _Node {
    uint32 dwType;  // see enum REFS_NODE_TYPE
    uint8 data[???];
} Node;

{% endhighlight %}


### Enums

#### REFS_LCB_STATE_FLAG

ReFS uses the `REFS_LCB_STATE_FLAG` values as flags that may be set within the `Lcb->dwState` bitfield.

{% highlight c %}

enum REFS_LCB_STATE_FLAG {
    LCB_STATE_DELETE_ON_CLOSE      = 0x1,   // potentially 0x2
    LCB_STATE_LINK_IS_GONE         = 0x2,   // potentially 0x1
    LCB_STATE_RTL_BUF_ALLOCATED    = 0x4,  
    LCB_STATE_EXACT_CASE_IN_TREE   = 0x8,   // potentially 0x10 
    LCB_STATE_IGNORE_CASE_IN_TREE  = 0x10,  // potentially 0x8
    LCB_STATE_VALID_HASH_VALUE     = 0x20
};

{% endhighlight %}

#### REFS_VCB_STATE_FLAG

ReFS uses the `REFS_VCB_STATE_FLAG` values as flags that may be set within the `Vcb->dwState` bitfield.

{% highlight c %}

enum REFS_VCB_STATE_FLAG {
    VCB_STATE_DELETE_UNDERWAY  = 0x2000,
    VCB_STATE_MOUNT_COMPLETED  = 0x10000000
};

{% endhighlight %}

#### REFS_FCB_STATE_FLAG

ReFS uses the `REFS_FCB_STATE_FLAG` values as flags that may be set within the `Fcb->dwState` bitfield.

{% highlight c %}

enum REFS_FCB_STATE_FLAG {
    FCB_STATE_FILE_DELETED               = 0x1,
    FCB_STATE_SYSTEM_FILE                = 0x100,
    FCB_STATE_USN_JOURNAL                = 0x8000,
    FCB_STATE_TABLE_CACHING_INITIALIZED  = 0x10000
};

{% endhighlight %}

#### REFS_FCB_FLAG

ReFS uses the `REFS_FCB_FLAG`  values as flags that may be set within the `Fcb->bFlags` bitfield.

{% highlight c %}

enum REFS_FCB_FLAG {
    FCB_FLAG_SHARED_FCB  = 1
};

{% endhighlight %}

#### REFS_SCB_STATE_FLAG

ReFS uses the `REFS_SCB_STATE_FLAG` values as flags that may be set within the `Scb->dwState` bitfield.

{% highlight c %}

enum REFS_SCB_STATE_FLAG {
    SCB_STATE_UNNAMED_DATA  = 0x10,
    SCB_STATE_OWNS_FILE_CACHE  = 0x400
};

{% endhighlight %}

#### REFS_FCB_INFO_FLAGS

ReFS uses the `REFS_FCB_INFO_FLAGS` values as flags that may be set within the `Fcb->dwInfo` bitfield.

{% highlight c %}

enum REFS_FCB_INFO_FLAGS {
    FCB_INFO_DIRECTORY  = 0x10000000
};

{% endhighlight %}

#### REFS_OBJECT_ID

ReFS uses 64bit object IDs to refer to objects such as files and directories. There are a few object IDs with hardcoded meaning. Object ID 0x600 is an example of this that refers to the root directory of the file system.

{% highlight c %}

enum REFS_OBJECT_ID {
    REFS_OBJECT_UNKNOWN_1   = 0x500,
    REFS_OBJECT_UNKNOWN_2   = 0x520,
    REFS_ROOT_DIRECTORY_ID  = 0x600,
    REFS_OBJECT_UNKNOWN_3   = 0x700   // 0x700 and above are system object IDs?
};

{% endhighlight %}

####

{% highlight c %}

{% endhighlight %}

####

{% highlight c %}

{% endhighlight %}


