from string import Template


def create_writer_prompt(title: str):
    template_content = open("templates/deepseek_writer_template.md").read()
    t = Template(template_content)
    prompt = t.substitute(title=title)
    return prompt


if __name__ == "__main__":
    print(create_writer_prompt("股票交易中最重要的参考指标是什么？"))
