"""
Example templates for testing
"""

# Basic Card Template
BASIC_TEMPLATE = {
    'name': 'Basic',
    'qfmt': '''
<div class="front">
    {{Front}}
</div>
''',
    'afmt': '''
<div class="back">
    {{FrontSide}}
    <hr>
    {{Back}}
</div>
''',
    'css': '''
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}

.front {
    padding: 20px;
}

.back {
    padding: 20px;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 20px 0;
}
'''
}

# Cloze Template
CLOZE_TEMPLATE = {
    'name': 'Cloze',
    'qfmt': '''
<div class="cloze">
    {{cloze:Text}}
</div>
''',
    'afmt': '''
<div class="cloze">
    {{cloze:Text}}
</div>
{{#Extra}}
<hr>
<div class="extra">
    {{Extra}}
</div>
{{/Extra}}
''',
    'css': '''
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
    padding: 20px;
}

.cloze {
    font-weight: bold;
}

.cloze .cloze-inactive {
    color: blue;
}

.extra {
    margin-top: 20px;
    color: #666;
    font-size: 16px;
}
'''
}

# Advanced Card with Image
ADVANCED_TEMPLATE = {
    'name': 'Advanced',
    'qfmt': '''
<div class="question">
    <h2>{{Title}}</h2>
    {{#Image}}
    <div class="image-container">
        <img src="{{Image}}" alt="Question Image">
    </div>
    {{/Image}}
    <div class="question-text">
        {{Question}}
    </div>
    {{#Hint}}
    <details>
        <summary>Show Hint</summary>
        <div class="hint">{{Hint}}</div>
    </details>
    {{/Hint}}
</div>
''',
    'afmt': '''
<div class="answer">
    {{FrontSide}}
    <hr>
    <div class="answer-text">
        {{Answer}}
    </div>
    {{#Explanation}}
    <div class="explanation">
        <strong>Explanation:</strong><br>
        {{Explanation}}
    </div>
    {{/Explanation}}
    {{#Tags}}
    <div class="tags">
        Tags: {{Tags}}
    </div>
    {{/Tags}}
</div>
''',
    'css': '''
.card {
    font-family: "Segoe UI", Tahoma, sans-serif;
    font-size: 18px;
    text-align: center;
    color: #333;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 30px;
    border-radius: 10px;
}

h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 24px;
}

.image-container {
    margin: 20px 0;
}

.image-container img {
    max-width: 100%;
    max-height: 400px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.question-text, .answer-text {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin: 15px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

details {
    margin-top: 15px;
    background: #fff3cd;
    padding: 10px;
    border-radius: 5px;
    cursor: pointer;
}

summary {
    font-weight: bold;
    color: #856404;
}

.hint {
    margin-top: 10px;
    padding: 10px;
    background: white;
    border-radius: 5px;
}

hr {
    border: none;
    border-top: 2px solid #ddd;
    margin: 25px 0;
}

.explanation {
    background: #d4edda;
    border-left: 4px solid #28a745;
    padding: 15px;
    margin: 15px 0;
    text-align: left;
    border-radius: 5px;
}

.tags {
    margin-top: 20px;
    font-size: 14px;
    color: #6c757d;
    font-style: italic;
}

/* Night mode */
.night_mode .card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #e0e0e0;
}

.night_mode h2 {
    color: #64b5f6;
}

.night_mode .question-text,
.night_mode .answer-text {
    background: #2d2d2d;
    color: #e0e0e0;
}

.night_mode .explanation {
    background: #1e3a1e;
    border-left-color: #4caf50;
    color: #a5d6a7;
}
'''
}

# All example templates
EXAMPLE_TEMPLATES = [
    BASIC_TEMPLATE,
    CLOZE_TEMPLATE,
    ADVANCED_TEMPLATE
]
