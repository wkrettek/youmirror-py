from youmirror.core import FileTree

ft = FileTree()
ft.from_json('./example.json')
ft.download_single('https://www.youtube.com/watch?v=Pa_HT9vQiLw&list=PLBZw8Bdva63UAhbdAlbbYotegKhUMeSzN&index=1')