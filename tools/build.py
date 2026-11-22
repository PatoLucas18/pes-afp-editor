#!/usr/bin/env python3
"""Arma app/EditorAFP.html (un solo archivo) uniendo src/editor.template.html y src/styles.css.
Uso:  python tools/build.py
"""
import pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
tpl = (root / 'src' / 'editor.template.html').read_text(encoding='utf-8')
css = (root / 'src' / 'styles.css').read_text(encoding='utf-8')
if '/*CSS*/' not in tpl:
    sys.exit('Falta el marcador /*CSS*/ en la plantilla')
out = root / 'app' / 'EditorAFP.html'
out.write_text(tpl.replace('/*CSS*/', css), encoding='utf-8', newline='\n')
print('OK', out, out.stat().st_size, 'bytes')
