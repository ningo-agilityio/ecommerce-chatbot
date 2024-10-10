from typing import Dict, TypedDict, Union

def get_assert(output: str, context) -> Union[bool, float, Dict[str, Any]]:
    print('Test GitHub flow')
    print('Prompt:', context['prompt'])
    print('Vars', context['vars']['topic'])

    # This return is an example GradingResult dict
    return {
      'pass': True,
      'score': 0.6,
      'reason': 'Looks good to me',
    }