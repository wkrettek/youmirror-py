# Pytube to yt-dlp Migration Plan

## Description
Replace pytube functionality with yt-dlp by modifying the function bodies in tuber.py. Keep the same function signatures and return types to maintain compatibility with core.py.

## Steps

### Step 1: Replace tuber.py function implementations
- [ ] `link_type(url)` - Determine if URL is channel/playlist/single
    - [ ] Use yt-dlp to extract info and check `_type` field
- [ ] `link_id(url)` - Extract ID from URL  
    - [ ] Use yt-dlp's extracted info['id']
- [ ] `yt_to_type_string(yt)` - Convert info dict type to string
    - [ ] Check info dict's '_type' field
- [ ] `get_metadata(yt)` - Extract metadata from info dict
    - [ ] Pull relevant fields from yt-dlp info dict
- [ ] `is_available(yt)` - Check if video is available
    - [ ] Check availability in info dict
- [ ] `new_pytube(url)` - Create info dict from URL
    - [ ] Use YoutubeDL().extract_info()
- [ ] `wrap_url(url, object)` - Adapt or remove
- [ ] `get_id(yt)` - Get ID from info dict
    - [ ] Return info['id']
- [ ] `get_name(yt)` - Get title/name from info dict
    - [ ] Return info['title'] or info['uploader']
- [ ] `get_url(yt)` - Get clean URL from info dict
    - [ ] Return info['webpage_url']
- [ ] `get_children(yt)` - Get video URLs from channel/playlist
    - [ ] Return URLs from info['entries']

### Step 2: Update core.py cache handling
- [ ] Modify cache to store yt-dlp info dicts instead of pytube objects
- [ ] Update get_pytube() to return info dicts

### Step 3: Handle type checking
- [ ] Replace isinstance/type checks for YouTube/Channel/Playlist objects
- [ ] Use info dict '_type' field instead

### Step 4: Test functionality
- [ ] Test single video URLs
- [ ] Test playlist URLs
- [ ] Test channel URLs
- [ ] Verify metadata extraction works correctly

## Notes
- Keep function signatures the same for compatibility
- Info dicts will replace pytube objects throughout
- Use extract_flat=True for faster playlist/channel extraction when only URLs needed
- Cache will store info dicts with URL as key