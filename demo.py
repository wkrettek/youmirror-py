from youmirror.core import YouMirror
import youmirror.databaser as databaser

ym = YouMirror()
ym.from_json('./example.json')
ym.sync('./example.json')
# databaser.create_db('./youmirror.db')