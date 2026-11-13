"""Insert data.json into template.html and write the standalone index.html."""
d = open('data.json').read().replace('</', '<\\/')
page = open('template.html').read().replace('__DATA__', d)
head = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>\n')
open('index.html', 'w').write(head + page + '\n</body></html>\n')
print('index.html', len(page))
