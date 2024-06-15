import google.generativeai as genai

from swetter import GEMINI_API_KEY

comment_prompt = (
    "Hello. I’ll give you the content of the comment (can be in any language)."
    " You must return me only True if anywhere there is obscene language or insults, etc."
    " If this is not the case, just return False."
    " Comment content: {}"
)

post_block_prompt = (
    "Hello. I’ll give you the title of the post and the content of the post (can be in any language)."
    " You must return me only True if anywhere there is obscene language or insults, etc."
    " If this is not the case, just return False."
    " Post title: {}"
    " Post content: {}"
)

reply_block_prompt = (
    "Hello. I’ll give you the content of the reply (can be in any language)."
    " You must return me only True if anywhere there is obscene language or insults, etc."
    " If this is not the case, just return False."
    " Reply content: {}"
)

create_reply_promt = (
    "Hello. I’ll give you the  the title ot the post,"
    "content of the post and content of the comment (can be in any language)."
    "You must return the text of the response to this comment (in the same language as the comment),"
    " on behalf of the creator of the post "
    "Post title: {}"
    "Post content: {}"
    "Comment content: {}"
)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def get_data_from_gemini(comment_content=None, post_title=None, post_content=None, reply_content=None) -> str | None:
    '''
    Get data from Gemini model to determine if content needs to be blocked.
    Depending on the provided parameters, this function formats a prompt and sends it to the Gemini model.
    :param comment_content: Content of the comment to be checked (optional)
    :param post_title: Title of the post to be checked (optional)
    :param post_content: Content of the post to be checked (optional)
    :param reply_content: Content of the reply to be checked (optional)
    :return: Boolean indicating if the content needs to be blocked or None if an error occurred
    :raises ValueError: If none of the parameters are provided
    '''

    if comment_content:
        prompt = comment_prompt.format(comment_content)
    elif post_title and post_content:
        prompt = post_block_prompt.format(post_title, post_content)
    elif reply_content:
        prompt = reply_block_prompt.format(reply_content)
    else:
        raise ValueError("Invalid input parameters")

    response = model.generate_content(prompt)

    try:
        need_to_block = response.text.split(" ")[0] == "True"
    except Exception as e:
        print(f"Warning: Response did not contain text data. Error: {e}")
        need_to_block = None

    return need_to_block


def create_reply_by_gemini(post_title, post_content, comment_content) -> str | None:
    '''
    Create a reply using the Gemini model.
    This function formats a prompt using the post title, post content, and comment content,
    and sends it to the Gemini model to generate a reply.
    :param post_title: Title of the post
    :param post_content: Content of the post
    :param comment_content: Content of the comment
    :return: Generated reply text or None if an error occurred
    '''

    prompt = create_reply_promt.format(post_title, post_content, comment_content)

    response = model.generate_content(prompt)

    try:
        result = response.text.replace("\n", "")
    except:
        print("Warning: Response did not contain text data")
        result = None

    return result
