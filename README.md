# Insert Image from Latex

This [Zim](https://github.com/zim-desktop-wiki/zim-desktop-wiki "Zim - A Desktop Wiki Editor") plugin allows you to insert various images into a page, as long as [LaTeX](https://www.latex-project.org/ "LaTeX – A document preparation system") scripts can be converted to these images. In other words, this Zim plugin will enable you to insert LaTeX scripts into a page but showing as an image.

# Installation 

```bash
# step 1 - install dependencies
apt-get install latex divpng

# step 2 - install this plugin
git clone http://this/repo.git ~/.local/share/zim/plugins/insert_latex/

# step 3 - restart Zim to load this plugin

# step 4 - enable this plugin
# In Edit > Preferences > Plugins tab, you can now tick Insert Image form LaTeX.

```

# Template

```latex
\documentclass[
    convert={
        convertexe={convert},
        command=\unexpanded{{
            \convertexe \space 
            -density \density \space 
            \infile \space 
            -resize \size \space 
            \outfile}},
        density=800,size=800x600,outext=.png
    },
    border={.5 .5 .5 2mm}
]{standalone}

\usepackage{bytefield}
\usepackage{graphicx}

\begin{document}
    \begin{bytefield}{32}
    % do some stuff
    \end{bytefield}
\end{document}
```

# Example 

## LaTeX bytefield 

With the following LaTeX scripts:
```latex
\documentclass[
    convert={
        convertexe={convert},
        command=\unexpanded{{
            \convertexe \space 
            -density \density \space 
            \infile \space 
            -resize \size \space 
            \outfile}},
        density=800,size=800x600,outext=.png
    },
    border={.5 .5 .5 2mm}
]{standalone}

\usepackage{bytefield}
\usepackage{graphicx}

\begin{document}
    \begin{bytefield}[bitwidth=1.5em, bitheight=\widthof{~AVL~}, endianness=big]{32}
        \bitheader{0-24,31} \\        
        & \bitbox{8}{Base (31-24)} & \bitbox{1}{G} & \bitbox{1}{\rotatebox{90}{D/B}}
        & \bitbox{1}{L} & \bitbox{1}{\rotatebox{90}{AVL}} & \bitbox{4}{Limit (19-16)}
        & \bitbox{1}{P} & \bitbox{2}{DPL} & \bitbox{1}{S} & \bitbox{4}{TYPE}
        & \bitbox{8}{Base (23-16)} 
    \end{bytefield}
\end{document}
```

you can get this in zim pages:

![gdt](data/latex.png)

