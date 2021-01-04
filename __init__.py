import glob

from zim.plugins import PluginClass
from zim.plugins.base.imagegenerator import \
    ImageGeneratorClass, BackwardImageGeneratorObjectType

from zim.fs import File, TmpFile
from zim.applications import Application, ApplicationError

# TODO put these commands in preferences
latex_cmd = ('latex', '-shell-escape', '-halt-on-error')
convert_cmd = ('convert', )


class InsertLatexPlugin(PluginClass):
    plugin_info = {
        'name': 'Insert Image from LaTeX',  # T: plugin name
        'description': '''\
This plugin provides an Latex editor for zim based on Latex.
''',  # T: plugin description
        'help': 'REAMME.md',
        'author': 'k4nzdroid@163.com',
    }

    @classmethod
    def check_dependencies(klass):
        has_latex = Application(latex_cmd).tryexec()
        has_convert = Application(convert_cmd).tryexec()
        return (has_latex and has_convert), \
               [('latex', has_latex, True), ('convert', has_convert, True)]


class BackwardLatexImageObjectType(BackwardImageGeneratorObjectType):
    name = 'image+latex'
    label = 'Image from LaTeX'  # T: menu item
    syntax = 'latex'
    scriptname = 'latex.tex'
    imagefile_extension: str = '.png'

    def deprecated_format_latex(self, dumper, attrib, data):
        if attrib['src'] and not attrib['src'] == '_new_':
            script_name = attrib['src'][:-3] + 'tex'
            script_file = dumper.linker.resolve_source_file(script_name)
            if script_file.exists():
                text = script_file.read().strip()
                return ['\\begin{math}\n', text, '\n\\end{math}']

        raise ValueError('missing source')  # parent class will fall back to image


class LatexGenerator(ImageGeneratorClass):

    def __init__(self, plugin, notebook, page):
        ImageGeneratorClass.__init__(self, plugin, notebook, page)
        self.texfile = TmpFile('latex.tex')
        print('[PLUGINS:INSERT LATEX] text file: %s' % self.texfile)

    def generate_image(self, text):

        if isinstance(text, str):
            text = text.splitlines(True)
        text = (line for line in text if line and not line.isspace())
        text = ''.join(text)
        print('[PLUGINS:INSERT LATEX] text written >>>%s<<<' % text)

        # Write to tmp file
        self.texfile.write(text)
        print('[PLUGINS:INSERT LATEX] read from file >>>%s<<<' % self.texfile.read())

        # Call latex
        logfile = File(self.texfile.path[:-4] + '.log')  # len('.tex') == 4
        print("[PLUGINS:INSERT LATEX] >>>", self.texfile, logfile)

        try:
            latex = Application(latex_cmd)
            latex.run((self.texfile.basename,), cwd=self.texfile.dir)
        except ApplicationError:
            print("[PLUGINS:INSERT LATEX] ApplicationError")
            return None, logfile

        png_file = File(self.texfile.path[:-4] + '.png')  # len('.tex') == 4

        return png_file, logfile

    def cleanup(self):
        path = self.texfile.path
        for path in glob.glob(path[:-4] + '.*'):
            File(path).remove()
