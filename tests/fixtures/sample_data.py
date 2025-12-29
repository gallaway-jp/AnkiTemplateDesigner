"""
Fixture data for tests
"""

# Sample Anki note types for testing
SAMPLE_NOTE_TYPES = {
    'basic': {
        'name': 'Basic',
        'id': 1234567890,
        'css': '.card { font-family: arial; font-size: 20px; }',
        'tmpls': [
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}',
                'ord': 0
            }
        ],
        'flds': [
            {'name': 'Front', 'ord': 0},
            {'name': 'Back', 'ord': 1}
        ]
    },
    'basic_reversed': {
        'name': 'Basic (and reversed card)',
        'id': 1234567891,
        'css': '.card { font-family: arial; font-size: 20px; }',
        'tmpls': [
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}',
                'ord': 0
            },
            {
                'name': 'Card 2',
                'qfmt': '{{Back}}',
                'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}',
                'ord': 1
            }
        ],
        'flds': [
            {'name': 'Front', 'ord': 0},
            {'name': 'Back', 'ord': 1}
        ]
    },
    'cloze': {
        'name': 'Cloze',
        'id': 1234567892,
        'css': '.card { font-family: arial; font-size: 20px; }',
        'tmpls': [
            {
                'name': 'Cloze',
                'qfmt': '{{cloze:Text}}',
                'afmt': '{{cloze:Text}}<br>{{Extra}}',
                'ord': 0
            }
        ],
        'flds': [
            {'name': 'Text', 'ord': 0},
            {'name': 'Extra', 'ord': 1}
        ]
    }
}

# Sample HTML templates
SAMPLE_HTML_TEMPLATES = {
    'simple': '<div class="card">{{Front}}</div>',
    'styled': '''
        <div class="card">
            <div class="question">{{Front}}</div>
            <div class="answer">{{Back}}</div>
        </div>
    ''',
    'with_image': '''
        <div class="card">
            <div class="text">{{Word}}</div>
            <img src="{{Image}}" />
            <div class="translation">{{Translation}}</div>
        </div>
    ''',
    'complex': '''
        <div class="card">
            <div class="header">
                <h1>{{Title}}</h1>
                <span class="subtitle">{{Subtitle}}</span>
            </div>
            <div class="content">
                <div class="main">{{Content}}</div>
                <div class="side">{{Extra}}</div>
            </div>
            <div class="footer">{{Footer}}</div>
        </div>
    '''
}

# Sample CSS
SAMPLE_CSS = {
    'basic': '''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
    ''',
    'styled': '''
        .card {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .question {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .answer {
            font-size: 18px;
            color: #333;
        }
    ''',
    'colorful': '''
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
        }
        
        .text {
            font-size: 28px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
    '''
}
