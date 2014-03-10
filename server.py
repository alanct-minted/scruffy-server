"""
 1. Install Scruffy
 2. Run server:

        $ pip install bottle
        $ python server.py

 3. Browse http://localhost:8080/

TODO: Detect and report invalid UML inputs.
"""
from bottle import route, run, template, response, BaseResponse
from subprocess import check_output
from tempfile import SpooledTemporaryFile

@route('/image/<uml:path>')
def suml(uml):
    # Create a memory file with the textual UML.
    uml = uml.replace('\n', ',') or ' '

    f = SpooledTemporaryFile()
    f.write(bytes(uml, 'UTF-8'))
    f.seek(0)

    # Execute Scruffy `suml`.
    try:
        png = check_output(['suml', '--scruffy', '--png'], stdin=f)
    finally:
        f.close()

    # Server the generated image.
    response.content_type = 'image/png'
    return png

@route('/')
@route('/edit/')
@route('/edit/<uml:path>')
def index(uml='// Cool Class Diagram,[ICustomer|+name;+email|]^-[Customer],[Customer]<>-orders*>[Order],[Order]++-0..*>[LineItem],[Order]-[note:Aggregate root.]'):
    uml = uml.replace(',', '\n')
    return template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scruffy</title>
            <script type="text/javascript" src="//code.jquery.com/jquery-2.1.0.min.js"></script>
            <script type="text/javascript" src="//code.jquery.com/ui/1.10.4/jquery-ui.min.js"></script>
            <link rel="stylesheet" href="//code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css">
            <style>
            form {
                display: inline-block;
            }
            textarea {
                background: #ffe;
            }
            img {
                vertical-align: top;
            }
            </style>
        </head>
        <body>
            <form>
                <textarea name="uml" rows="10" cols="80" autofocus="autofocus">{{uml}}</textarea>
                <div>See <a href="https://github.com/aivarsk/scruffy/blob/master/README.rst" target="_blank">Scruffy syntax</a>.</div>
            </form>
            <a href="#" title="Click to edit"><img src="" /></a>
            <script type="text/javascript">
            // Update when the input text is changed (after a short delay).
            var update = function() {
              var uml = $('textarea').val().replace(/(\\r\\n|\\n|\\r)/gm, ',');
              $('img').attr('src', '/image/' + encodeURIComponent(uml));
              window.history.pushState('Scruffy', 'Scruffy', '/edit/' + encodeURIComponent(uml));
            };
            var delay = (function() {
              var timer = 0;
              return function(callback, ms){
                clearTimeout (timer);
                timer = setTimeout(callback, ms);
              };
            })();
            $('textarea').on('input', function() {
              delay(update, 300);
            });

            var show = function() {
              $('form').slideDown(200);
              $('textarea').focus();
              return false;
            };

            var hide = function() {
              $('form').slideUp(200);
            };

            // Limit the textarea size.
            $('textarea').resizable({
              minHeight: 100,
              minWidth: 300,
              handles: 'se'
            }).parent().css('padding-bottom', '0');

            // Display input on click.
            $('img').click(show);

            // Display input on key down, except ESC.
            $('html').keydown(function(e) {
              if (e.keyCode == 27) {
                hide();
              } else {
                show();
              }
            });

            // Hide input when clicking outside.
            $('html').click(function() {
              hide();
            });
            $('textarea').click(function() {
              return false;
            });

            update();
            hide();
            </script>
        </body>
        </html>
        """,
        uml=uml)

run(host='0.0.0.0', port=8080)
