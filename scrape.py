#!/usr/bin/env python
"""
Grabs the content of the GFDL work "The Future We Deserve" from
http://www.appropedia.org/TheFWD_index and turns it into an ePub book.
"""
import os
import logging
import requests
from datetime import date
from uuid import uuid4
from lxml.html import fromstring, tostring
from shutil import copyfile
from jinja2 import Environment, FileSystemLoader


DOMAIN = "http://www.appropedia.org"
START = DOMAIN+"/TheFWD_index"
TITLE = "The Future We Deserve"
OUTPUT = "tfwd"
REMOVE = ['#siteSub', '#contentSub', '#jump-to-nav', '.editsection',
          '.printfooter', '.catlinks', '.visualClear']


# set up the logger
logger = logging.getLogger("epub")
logger.setLevel(logging.DEBUG)
logfile_handler = logging.FileHandler('epub.log')
logfile_handler.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - "\
                               "%(message)s")
logfile_handler.setFormatter(log_format)
logger.addHandler(logfile_handler)


def grab_html(target):
    """
    Given a URL will return an lxml HTML element object.
    """
    raw = requests.get(target)
    return fromstring(raw.text)


def scrape_index(target):
    """
    Takes the start page URL and extracts an ordered list of URLS that point
    to each of the chapters (sub sections) of the work.
    """
    logger.info('Getting index...')
    html = grab_html(START)
    items = [i.attrib['href'] for i in html.cssselect('#content li a')]
    logger.info('Got %d items' % len(items))
    return items


def scrape_chapter(target, directory):
    """
    Given a URL to a chapter (sub section) will scrape the content from the
    endpoint and produce a dict object shaped as follows:

    {
        'title': '...',
        'content': <HTML CONTENT OF ARTICLE>,
    }
    """
    logger.info('Processing %s' % target)
    html = grab_html(DOMAIN+target)
    header = html.cssselect('#firstHeading')[0]
    result = {}
    result['title'] = header.text
    body_content = html.cssselect('#bodyContent')[0]
    body_content.attrib['id'] = header.text.strip().replace(' ', '')
    # remove bits and bobs
    for r in REMOVE:
        to_remove = body_content.cssselect(r)
        for element in to_remove:
            element.drop_tree()
    # Process images
    image_tags = body_content.cssselect('img')
    for i in image_tags:
        src = i.attrib['src']
        filename = src.rsplit('/', 1)
        if len(filename) == 2:
            filename = filename[1]
        else:
            break
        logger.info('Grabbing image from %s' % src)
        raw = requests.get(DOMAIN+src)
        output = open(os.path.join(directory, 'OEBPS', 'images', filename),
            'wb')
        output.write(raw.content)
        output.close()
        i.attrib['src'] = 'images/%s' % filename
    result['content'] = tostring(body_content)
    return result


def zipEpubDirectory(name):
    """
    Given a temporary directory containing the files for an EPUB book, this
    method zips it up correctly.
    """
    logger.info('Zipping up EPUB')
    os.chdir(name)
    os.system("zip -0Xq %s.epub mimetype" % name)
    os.system("zip -Xr9Dq %s.epub *" % name)
    os.system("cp %s.epub .." % name)


def createEpubDirectory(directory):
    """
    Create a temporary directory for the EPUB content
    """
    logger.info('Creating EPUB in temporary directory %s' % directory)
    os.mkdir(directory)
    template_directories = []
    for templates in os.walk('templates'):
        template_directories.append(templates[0])
        root = templates[0].replace('templates', directory)
        for child_directory in templates[1]:
            os.mkdir(os.path.join(root, child_directory))


def createEpubFileStructure(directory, chapters):
    """
    Use templates to create a temporary directory structure of the EPUB
    content
    """
    template_directories = []
    for templates in os.walk('templates'):
        template_directories.append(templates[0])
    env = Environment(loader=FileSystemLoader(template_directories))
    context = {
        'title': TITLE,
        'uuid': str(uuid4()),
        'date': date.today().isoformat(),
        'items': chapters
    }
    # Copy over and render the files via Jinja2
    for templates in os.walk('templates'):
        root = templates[0].replace('templates', directory)
        for template_file in templates[2]:
            logger.info('Processing template %s' % template_file)
            # use these as templates to be save to the appropriate location
            # in the temporary directory
            if template_file.endswith('.png'):
                # just copy over the cover
                src = os.path.join(templates[0], template_file)
                dest = os.path.join(root, template_file)
                copyfile(src, dest)
            else:
                template = env.get_template(template_file)
                rendered = template.render(context)
                output = open(os.path.join(root, template_file), 'w')
                output.write(rendered.encode('utf-8'))
                output.close()


if __name__ == '__main__':
    logger.info(TITLE)
    createEpubDirectory(OUTPUT)
    chapter_urls = scrape_index(START)
    chapters = []
    for chapter in chapter_urls:
        chapters.append(scrape_chapter(chapter, OUTPUT))
    createEpubFileStructure(OUTPUT, chapters)
    zipEpubDirectory(OUTPUT)
    logger.info('DONE')
