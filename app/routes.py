from flask import render_template, request
from app import app
from app.forms import InputForm 
from run_saved_model import run_model_main

@app.route('/', methods=['GET', 'POST'])
def index():
  form = InputForm(request.form)
  if request.method == 'GET':
    return render_template('input.html', form=form)
  elif request.method == 'POST' and form.validate():
    response = run_model_main(form.claim.data, form.document.data)
    data = parse_response(response)
    return render_template('output.html', data=data)
  else:
    return "ERROR NOT SUPPORTED"


def parse_response(response):
  '''
  Given the response from the saved model as provided in run_saved_model.py, this function parses that response
  and reshapes it into a form which is easily consumable by the templates.
  '''
  data = {}

  data['overall_data'] = {
    "claim": response[0][0],
    "document": response[1][0],
    "related_unrelated_pred": response[2][0],
    "related_unrelated_logit": round_decimals(response[3][0]),
    "three_label_pred": response[4][0],
    "three_label_logit": round_decimals(response[5][0]),
    "color": determine_color(response[3][0], response[5][0]),
    "logit_colors": get_logit_colors(response[3][0] + response[5][0]) 
  }

  data['sentence_data'] = []
  for i in range(1, len(response[0])):
      data['sentence_data'].append({
        "num": i,
        "claim": response[0][i],
        "sentence": response[1][i],
        "related_unrelated_pred": response[2][i],
        "related_unrelated_logit": round_decimals(response[3][i]),
        "three_label_pred": response[4][i],
        "three_label_logit": round_decimals(response[5][i]),
        "color": determine_color(response[3][i], response[5][i]),
        "logit_colors": get_logit_colors(response[3][i] + response[5][i])
      })

  return data;


def round_decimals(logits):
    '''
    Rounds a list of numbers to the nearest hundreth. 
    '''
    return [round(logit, 2) for logit in logits]


def determine_color(rulogits, addlogits):
    '''
    Based on the related/unrelated logits and the agree/disagree/discuss logits, this function determines
    the appropriate color and intensity associated with the related text.
    '''
    colors = get_logit_colors(rulogits + addlogits)
    if rulogits[1] >= rulogits[0]:
        return colors[1]
    else:
        if addlogits[0] >= addlogits[1]:
            if addlogits[0] >= addlogits[2]:
                return colors[2]
            else:
                return colors[4]
        else:
            if addlogits[1] >= addlogits[2]:
                return colors[3]
            else:
                return colors[4]
    
def intensity(logit):
    '''
    Defines 5 intensity buckets uniformly distributed from 0 to 1.
    '''
    return int(logit//0.2) + 1;

def get_logit_colors(logits):
    '''
    Given a set of logits, assumed to be in the related, unrelated, agree, disagree, discuss order, the appropriate
    color and intensity combinations to represent the results are calculated.
    '''
    # related, unrelated, agree, disagree, discuss
    base_colors = [None, "grey", 'blue', 'red', 'purple']
    colors = []
    for i in range(len(logits)):
        if base_colors[i] is None:
            colors.append("")
            continue
        colors.append(base_colors[i] + str(intensity(logits[i])))
    return colors

