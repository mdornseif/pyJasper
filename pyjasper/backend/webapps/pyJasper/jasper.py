#!/usr/bin/env python
# encoding: utf-8
"""
jasper.py - pyJasper Servlet

Created by Maximillian Dornseif on 2007-09-09.
Copyright (c) 2007 HUDORA GmbH. All rights reserved.
"""

import sys
sys.path.extend(['.'])

import java.lang
from javax.servlet.http import HttpServlet
from org.apache.commons.fileupload.servlet import ServletFileUpload
from org.apache.commons.fileupload.disk import DiskFileItemFactory
import XmlJasperInterface

import simplejson

__revision__ = '$Revision$'


class jasper(HttpServlet):
    """Servlet for rendering JasperReport reports.
    
    The servlet keeps no state at all. You have to supply it with an
    XML datasource, an XPath expression for that datasource and
    the JRXML report design. You get back the generated PDF or an
    plain text error message.
    
    The respective data has to be submitted via the form variables
    'xpath', 'design' and 'xmldata'.
    
    To try it out you can use curl. E.g.
    curl -X POST --form xpath=//lieferscheine/lieferschein 
                 --form design=@reports/Lieferschein.jrxml 
                 --form xmldata=@sample-xml/Lieferschein.xml 
                 http://localhost:8080/pyJasper/jasper.py > test.pdf
    """
    
    def doGet(self, request, response):
        """Handle GET requests by just redirecting to doPost()."""
        # we use the same handler for GET and POST. I wonder:
        # actually GET is correct since there is no state change on the server
        # but POST can handle more data
        self.doPost(request, response)
    
    def doPost(self, request, response):
        """Generates a PDF with JasperReports. To be called with:
           
           xmldata: XML data Source for JasperReports
           xpath:   XPATH Expression for selecting rows from the datasource
           design:  JasperReports JRXML Report Design
           designs: JasperReports JRXML Report Design when using subreports.
        """
        
        print "processing request"

        data = {'xpath': request.getParameter('xpath'),
                'design': request.getParameter('design'),
                'designs':request.getParameter('designs'),
                'xmldata': request.getParameter('xmldata')}
        
        if ServletFileUpload.isMultipartContent(request):
            servlet_file_upload = ServletFileUpload(DiskFileItemFactory())
            files = servlet_file_upload.parseRequest(request)
            fiterator = files.iterator()
            while fiterator.hasNext():
                file_item = fiterator.next()
                data[file_item.getFieldName()] = str(java.lang.String(file_item.get()))

        if data['designs']:
            data['designs'] = simplejson.loads(data['designs'])

        if not data['designs']:
            data['designs'] = {'main': data['design']}

        out = response.getWriter()
        if not data['xpath']:
            out.println('No valid xpath: %r\nDocumentation:' % data['xpath'])
            out.println(self.__doc__)
        elif not data['designs']:
            out.println('No valid design: %r\nDocumentation:' % data['designs'])
            out.println(self.__doc__)
        elif not data['xmldata']:
            out.println('No valid xmldata: %r\nDocumentation:' % data['xmldata'])
            out.println(self.__doc__)
        else:
            response.setContentType("application/pdf")
            jaspergenerator = XmlJasperInterface.JasperInterface(data['designs'], data['xpath'])
            out.write(jaspergenerator.generate(data['xmldata'], 'pdf'))
        out.close()
