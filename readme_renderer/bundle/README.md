# General purpose assets

## Generation of katex.min.js for V8

- The following steps can be made to **BUMP** the KaTeX version in the future:

```bash
    cd readme_renderer/bundle && \
    export KATEX_VERSION="0.16.9" && \
    wget "https://cdn.jsdelivr.net/npm/katex@${KATEX_VERSION}/dist/katex.mjs" && \
    sed -i '$ d' katex.mjs && \
    mv katex.mjs katex.js && \
    npm install --save-exact --save-dev esbuild && \
    ./node_modules/.bin/esbuild katex.js --minify --outfile=katex.min.js
```

## CSS used by KaTeX

- After inspecting the following stylesheet it becomes obvious we may or may not need to install some fonts on PyPI.
  
- While performing some local tests I haven't needed any special fonts, but in case  it ends up being necessary there is a client side script that can avoid the server setup all together.

```html
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.css" integrity="sha384-OH8qNTHoMMVNVcKdKewlipV4SErXqccxxlg6HC9Cwjr5oZu2AdBej1TndeCirael" crossorigin="anonymous">

    <script>
    window.WebFontConfig = {
        custom: {
        families: ['KaTeX_AMS', 'KaTeX_Caligraphic:n4,n7', 'KaTeX_Fraktur:n4,n7',
            'KaTeX_Main:n4,n7,i4,i7', 'KaTeX_Math:i4,i7', 'KaTeX_Script',
            'KaTeX_SansSerif:n4,n7,i4', 'KaTeX_Size1', 'KaTeX_Size2', 'KaTeX_Size3',
            'KaTeX_Size4', 'KaTeX_Typewriter'],
        },
    };
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/webfontloader@1.6.28/webfontloader.js" integrity="sha256-4O4pS1SH31ZqrSO2A/2QJTVjTPqVe+jnYgOWUVr7EEc=" crossorigin="anonymous"></script>
```
