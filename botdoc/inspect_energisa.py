import pymupdf

doc = pymupdf.open('modelo_energisa.pdf')
page = doc[0]
print("Page rect:", page.rect)
blocks = page.get_text('dict')['blocks']

for b in blocks:
    if 'lines' in b:
        for l in b['lines']:
            text = "".join(s['text'] for s in l['spans'])
            if any(k in text for k in ['MILENNA', 'PEDRO', '28610', 'CNPJ/CPF', 'FRIBURGO']):
                print(f"Line: {l['bbox']} -> {repr(text)}")
                for s in l['spans']:
                    print(f"   Span: {s['bbox']} | font: {s['font']} | size: {round(s['size'], 2)} | color: #{s['color']:06x} | text: {repr(s['text'])}")
