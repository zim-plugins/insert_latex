import glob, os

from zim.plugins import PluginClass
from zim.plugins.base.imagegenerator import \
    ImageGeneratorClass, BackwardImageGeneratorObjectType

from zim.newfs import LocalFile, TmpFile, localFileOrFolder
from zim.templates import Template
from zim.applications import Application, ApplicationError

# TODO put these commands in preferences
latexcmd = 'latex'
dvipngcmd = 'dvipng'

class InsertLatexPlugin(PluginClass):
    plugin_info = {
        'name': 'Insert Image from LaTeX',  # T: plugin name
        'description': '''\
This plugin provides an Latex editor for zim based on Latex.
''',  # T: plugin description
        'help': 'README.md',
        'author': 'k4nzdroid@163.com',
    }

    plugin_preferences = (
        # key, type, label, default
        ('dark_mode', 'bool', _('Use font color for dark theme'), False), # T: plugin preference
        ('font_size', 'choice', _('Font size'), "12pt", ("8pt", "9pt", "10pt", "11pt", "12pt", "14pt", "17pt", "20pt")), # T: plugin preference
        ('output_dpi', 'choice', _('Equation image DPI'), "120", ("96","120","150","200","300","400","600")), # T: plugin preference
    )

    @classmethod
    def check_dependencies(klass):
        has_latex = Application(latexcmd).tryexec()
        has_dvipng = Application(dvipngcmd).tryexec()
        return (has_latex and has_dvipng), \
                [('latex', has_latex, True), ('dvipng', has_dvipng, True)]


class BackwardLatexImageObjectType(BackwardImageGeneratorObjectType):
    name = 'image+latex'
    label = 'Image from LaTeX' # T: menu item
    syntax = 'latex'
    scriptname = 'latex.tex'
    widget_style = 'inline'

class LatexGenerator(ImageGeneratorClass):

    imagefile_extension = '.png'

    def __init__(self, plugin, notebook, page):
        ImageGeneratorClass.__init__(self, plugin, notebook, page)
        self.preferences = plugin.preferences
        self.template = Template(localFileOrFolder('templates/latexeditor.tex', os.path.dirname(__file__)))
        self.texfile = TmpFile('latex.tex')

    def get_default_text(self):
        text = []
        self.template.process(text, {
            'font_size': self.preferences['font_size'],
            'dark_mode': self.preferences['dark_mode']
        })
        text = ''.join(text)

        return text

    def generate_image(self, text):
        # Write to tmp file
        self.texfile.write(text)

        # Call latex
        logfile = LocalFile(self.texfile.path[:-4] + '.log')  # len('.tex') == 4
        #~ print(">>>", self.texfile, logfile)
        try:
            latex = Application('%s -no-shell-escape -halt-on-error' % (latexcmd))
            latex.run((self.texfile.basename,), cwd=self.texfile.parent())
        except ApplicationError:
            # log should have details of failure
            return None, logfile

        # Call dvipng
        dvifile = LocalFile(self.texfile.path[:-4] + '.dvi') # len('.tex') == 4
        pngfile = LocalFile(self.texfile.path[:-4] + '.png') # len('.tex') == 4
        dvipng = Application('%s -q -bg Transparent -T tight -D %s -o' % (dvipngcmd,self.preferences['output_dpi']))
        dvipng.run((pngfile, dvifile)) # output, input
        # No try .. except here - should never fail
        # TODO dvipng can start processing before latex finished - can we win speed there ?

        return pngfile, logfile

    def cleanup(self):
        path = self.texfile.path
        for path in glob.glob(path[:-4] + '.*'):
            LocalFile(path).remove()
