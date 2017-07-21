import webapp2
import logging
from webapp2_extras import jinja2

class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
      return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, template_args):
      self.response.write(self.jinja2.render_template(filename, **template_args))

    def handle_exception(self, exception, debug):
        # Log the error.
        
        logging.info('log exception next')
        logging.exception(exception)

        # Set a custom message.
        self.response.write(exception)

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)

        else:
            self.response.set_status(500)