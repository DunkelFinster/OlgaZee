#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#     P A G E B O T
#
#     Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens
#     www.pagebot.io
#     Licensed under MIT conditions
#
#     Supporting DrawBot, www.drawbot.com
#     Supporting Flat, xxyxyz.org/flat
# -----------------------------------------------------------------------------
#
#     site.py
#
import os
import shutil
import webbrowser

from pagebot.publications.publication import Publication
from pagebot.constants import URL_JQUERY
from pagebot.composer import Composer
from pagebot.typesetter import Typesetter
from pagebot.elements import *
from pagebot.conditions import *
from pagebot.toolbox.color import color, whiteColor, blackColor
from pagebot.toolbox.units import em, pt
from pagebot.elements.web.nanosite.siteelements import *

from css.nanostyle_css import cssPy

from pagebot.themes import *
#   BackToTheCity
#   BusinessAsUsual 
#   FairyTales 
#   FreshAndShiny 
#   IntoTheWoods 
#   SeasoningTheDish 
#   SomethingInTheAir 
#   WordlyWise
#   HappyHolidays
from pagebot.themes.basetheme import BaseTheme

class OlgaTheme(BaseTheme):
    NAME = 'Fantasy Red'
    BASE_COLORS = dict(
        base0=color(0.2, 0.2, 0.2), 
        base1=color(0.3, 0.2, 0.1), 
        base2=color(0.3, 0.2, 0.2), 
        base3=color(0.3, 0.2, 0.1), 
        base4=color(0.1, 0.1, 0.1), 
        base5=color(0.1, 0.1, 0.1), 
    )

Theme = OlgaTheme

theme = Theme('dark')
#theme = Theme('light')

SITE_NAME = 'OLGA ZEE' # Also used as logo

MD_PATH = 'Olga-Zee.com.md'
EXPORT_PATH = '_export/' + SITE_NAME # Export path for DO_FILE

VERBOSE = False

DO_PDF = 'Pdf' # Save as PDF representation of the site.
DO_FILE = 'File' # Generate website output in _export/SimpleSite and open browser on file index.html
DO_MAMP = 'Mamp' # Generate website in /Applications/Mamp/htdocs/SimpleSite and open a localhost
DO_GIT = 'Git' # Generate website and commit to git (so site is published in git docs folder.
EXPORT_TYPE = DO_MAMP

NUM_CONTENT = 2 # Number of content elements on a page.
NUM_SIDES = 1 # Number of side elements next to a main content element,

# Max image size of scaled cache (used mulitplied by resolution per image type DEFAULT_RESOLUTION_FACTORS
MAX_IMAGE_WIDTH = 800 


styles = dict(
    body=dict(
        fill=whiteColor,
        ml=9, mr=0, mt=0, mb=0,
        pl=em(3), pr=em(3), pt=em(3), pb=em(3),
        fontSize=pt(12),
        leading=em(1.4),
    ),
    br=dict(leading=em(1.4)
    ),
)

def makeNavigation(doc):
    """After all pages of the site are generated, we can use the compiled page tree
    from doc to let all Navigation elements build the menu for each page.
    """
    for pages in doc.pages.values():
        for page in pages:  
            navigation = page.select('Navigation')
            if navigation is not None:
                navigation.pageTree = doc.getPageTree() # Get a fresh one for each page

def makeTemplate(doc):

    # D E F A U L T

    default = Template('Default', context=doc.context)
    wrapper = Wrapper(parent=default) # Create main page wrapper
    
    header = Header(parent=wrapper) # Header to hold logo and navigation elements

    #logoString = doc.context.newString(SITE_NAME)
    Logo(parent=header, logo=SITE_NAME)
    BurgerButton(parent=header)

    # Responsive conditional menus
    Navigation(parent=header)
    MobileMenu(parent=header)

    # Just make a simple content container in this template.
    # Rest of content is created upon request in MarkDown
    Content(parent=wrapper) 

    # Default Footer at bottom of every page.
    Footer(parent=wrapper)

    """    
    # SlideShow https://www.bbslider.com
    group = Group(cssClass='slideshowgroup clearfix', parent=header)
    BareBonesSlideShow(h=300, w=300, cssId='SlideShow', parent=group, duration=0.7,
        startIndex=2, dynamicHeight=True, transition=BBS_SLIDE, 
        easing=CSS_EASE, frameDuration=4,
        pauseOnHit=True, randomPlay=False)
    BareBonesSlideSide(cssId='SlideSide', parent=group)

    # Content, root for all content containers such as 
    # Introduction, Main and Side.
    Content(parent=wrapper, cssId='Content')

    # Footer
    Footer(parent=wrapper)
    """

    doc.addTemplate('default', default)
    return default

def makeSite(styles, viewId):
    site = Site(styles=styles)
    doc = site.newDocument(viewId=viewId, autoPages=1, defaultImageWidth=MAX_IMAGE_WIDTH)
    
    doc.theme = theme

    view = doc.view
    view.resourcePaths = ('css','fonts','images','js')
    view.jsUrls = (
        URL_JQUERY, 
        #URL_MEDIA, 
        'js/sitemain.js', 
        'js/jquery.bbslider.min.js'
    )
    
    # Generate css by mapping theme.mood on cssPy 
    cssPath = 'css/nanostyle_py.css'
    doc.context.b.writeCss(cssPath, cssPy % theme.mood)

    view.cssUrls = (
        'css/jquery.bbslider.css',
        'fonts/webfonts.css', 
        'css/normalize.css', 
        cssPath,
    )

    # Make the all pages and elements of the site as empty containers, that then can
    # be selected and filled by the composer, using the galley content.
    # Of the MarkDown text can decide to create new elements inside selected elements.
    template = makeTemplate(doc)    

    page = doc[1]
    page.applyTemplate(template) # Copy element tree to page.

    # By default, the typesetter produces a single Galley with content and code blocks.    
    t = Typesetter(doc.context)
    galley = t.typesetFile(MD_PATH)
    
    # Create a Composer for this document, then create pages and fill content. 
    composer = Composer(doc)

    # The composer executes the embedded Python code blocks that indicate where content should go.
    # by the HtmlContext. Feedback by the code blocks is added to verbose and errors list
    targets = dict(doc=doc, page=page, template=template)
    composer.compose(galley, targets=targets)

    if VERBOSE:
        if targets['verbose']:
            print('Verbose\n', '\n'.join(targets['verbose']))
        # In case there are any errors, show them.
        if targets['errors']:
            print('Errors\n', '\n'.join(targets['errors']))
    
    # Find the navigation elements and fill them, now we know all the pages.
    makeNavigation(doc)

    return doc

if EXPORT_TYPE == DO_PDF: # PDF representation of the site
    doc = makeSite(styles=styles, viewId='Page')
    doc.solve() # Solve all layout and float conditions for pages and elements.
    doc.export(EXPORT_PATH + '.pdf')

elif EXPORT_TYPE == DO_FILE:
    doc = makeSite(styles=styles, viewId='Site')
    doc.export(EXPORT_PATH)
    openingPage = 'program-2019.html'
    os.system(u'/usr/bin/open "%s/%s"' % (EXPORT_PATH, openingPage))

elif EXPORT_TYPE == DO_MAMP:
    # Internal CSS file may be switched off for development.
    doc = makeSite(styles=styles, viewId='Mamp')
    mampView = doc.view
    MAMP_PATH = '/Applications/MAMP/htdocs/' 
    filePath = MAMP_PATH + SITE_NAME 
    if VERBOSE:
        print('Site path: %s' % MAMP_PATH)
    if os.path.exists(filePath):
        shutil.rmtree(filePath) # Comment this line, if more safety is required. In that case manually delete.
    doc.export(filePath)

    if not os.path.exists(filePath):
        print('The local MAMP server application does not exist. Download and install from %s.' % view.MAMP_SHOP_URL)
        os.system(u'/usr/bin/open %s' % view.MAMP_SHOP_URL)
    else:
        #t.doc.export('_export/%s.pdf' % NAME, multiPages=True)
        os.system(u'/usr/bin/open "%s"' % mampView.getUrl(SITE_NAME))

elif EXPORT_TYPE == DO_GIT and False: # Not supported for SimpleSite, only one per repository?
    # Make sure outside always has the right generated CSS
    doc = makeSite(styles=styles, viewId='Git')
    doc.export(EXPORT_PATH)
    # Open the css file in the default editor of your local system.
    os.system('git pull; git add *;git commit -m "Updating website changes.";git pull; git push')
    os.system(u'/usr/bin/open "%s"' % view.getUrl(DOMAIN))

else: # No output view defined
    print('Set EXPORTTYPE to DO_FILE or DO_MAMP or DO_GIT')

