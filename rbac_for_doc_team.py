import os
import re
import sys
import fnmatch

import yaml


role_or_binding = re.compile(r'^kind: *(Cluster)?Role(Binding)?$')
yml_extension = re.compile(r'^.*\.y[a]?ml(\.tmpl)$')


def wrap_golang_variables_with_quotes(lines_of_yaml):
    go_template = re.compile(r': *\{\{ *([\w". ]+) *\}\}')
    lines = []
    for line in lines_of_yaml:
        if go_template.search(line):
            lines.append(go_template.sub(r': \1', line))
        else:
            lines.append(line)

    return lines


def remove_golang_statements(lines_of_yaml):
    go_statement = re.compile(r'^ *\{\{-? *[\w". ]+ *-?\}\}.*$')
    lines = []
    for line in lines_of_yaml:
        if not go_statement.search(line):
            lines.append(line)

    return lines


def find_files_with_role_or_cluster_role_bindings(basedir):
    matches = []
    for root, directories, filenames in os.walk(basedir):
        for filename in fnmatch.filter(filenames, '*.y*ml*'):
            filepath = os.path.join(root, filename)
            if yml_extension.match(filepath):
                with open(filepath) as f:
                    for line in f.readlines():
                        if role_or_binding.match(line):
                            matches.append(filepath)
                            break

    return matches


def extract_role_bindings(filepath):
    separator = re.compile(r'^---$')
    go_template = re.compile(r'(\{\{ *[^ ]+ *\}\})')

    yaml_lines = []
    with open(filepath) as f:
        lines = f.readlines()
        print_lines = False
        for line in lines:
            if go_template.search(line):
                line = go_template.sub(r'"\1"', line)
            if role_or_binding.match(line):
                print_lines = True
            if separator.match(line):
                print_lines = False
            if print_lines:
                yaml_lines.append(line)


def extract_rbac_permissions(filepath):
    separator = re.compile(r'^---$')
    go_template = re.compile(r'(\{\{ *[^ ]+ *\}\})')

    yaml_lines = []
    with open(filepath) as f:
        lines = f.readlines()
        print_lines = False
        for line in lines:
            if go_template.search(line):
                line = go_template.sub(r'"\1"', line)
            if role_or_binding.match(line):
                print_lines = True
            if separator.match(line):
                print_lines = False
            if print_lines:
                yaml_lines.append(line)

        yaml_content = "".join(yaml_lines)
        yaml_data = yaml.load(yaml_content, Loader=yaml.Loader)
        print(f"### Bound to {yaml_data['kind']}")
        print(f"{yaml_data['metadata']['name']}")
        print("")
        print('#### API groups')
        for yaml_rule in yaml_data['rules']:
            if 'apiGroups' in yaml_rule:
                api_groups = ', '.join(yaml_rule['apiGroups'])
                if not api_groups:
                    api_groups = 'none'
                print(f"* {api_groups}")
                for resource in yaml_rule['resources']:
                    print(f"  * {resource} ({', '.join(yaml_rule['verbs'])})")


def yaml_load(filepath):
    with open(filepath) as f:
        lines = wrap_golang_variables_with_quotes(f.readlines())
        lines = remove_golang_statements(lines)
        return list(yaml.load_all("".join(lines), Loader=yaml.Loader))


def extract_cluster_and_role_bindings(filepaths):
    role_bindings = {}
    cluster_role_bindings = {}
    for fp in filepaths:
        yaml_docs = yaml_load(fp)
        for doc in yaml_docs:
            if doc['kind'] == 'RoleBinding':
                role_bindings[doc['roleRef']['name']] = []
                for subject in doc['subjects']:
                    if 'kind' in subject and subject['kind'] == 'ServiceAccount':
                        # structure: {role_binding_name : [service_account, service_account, ...]}
                        role_bindings[doc['roleRef']['name']].append(subject['name'])
            if doc['kind'] == 'ClusterRoleBinding':
                cluster_role_bindings[doc['roleRef']['name']] = []
                for subject in doc['subjects']:
                    if 'kind' in subject and subject['kind'] == 'ServiceAccount':
                        # structure: {cluster_role_binding_name : [service_account, service_account, ...]}
                        cluster_role_bindings[doc['roleRef']['name']].append(subject['name'])
    return role_bindings, cluster_role_bindings


def extract_roles_and_cluster_roles(filepaths):
    roles = {}
    cluster_roles = {}
    for fp in filepaths:
        yaml_docs = yaml_load(fp)
        for doc in yaml_docs:
            if doc['kind'] == 'Role':
                roles[doc['metadata']['name']] = doc['rules']
            if doc['kind'] == 'ClusterRole':
                cluster_roles[doc['metadata']['name']] = doc['rules']
    return roles, cluster_roles


def extract_markdown(roles, role_bindings, text):
    markdown_lines = []
    for role_name in sorted(roles.keys()):
        rules = roles[role_name]
        markdown_lines.append('')
        markdown_lines.append('### Service account')
        for service_account in role_bindings[role_name]:
            markdown_lines.append(f"* {service_account}")

        markdown_lines.append('')
        markdown_lines.append(f'### {text}')
        markdown_lines.append(role_name)

        markdown_lines.append('')
        markdown_lines.append('### API groups')
        for rule in rules:
            if 'apiGroups' in rule:
                for api_group in sorted(rule['apiGroups']):
                    if api_group == '':
                        markdown_lines.append('* none')
                    else:
                        markdown_lines.append(f"* {api_group}")
                for resource in sorted(rule['resources']):
                    markdown_lines.append(f"  * {resource} ({', '.join(sorted(rule['verbs']))})")
        markdown_lines.append('')
        markdown_lines.append('---')
    return markdown_lines


def main():
    filepaths = find_files_with_role_or_cluster_role_bindings('.')

    role_bindings, cluster_role_bindings = extract_cluster_and_role_bindings(filepaths)
    roles, cluster_roles = extract_roles_and_cluster_roles(filepaths)

    markdown_lines = [
        '---',
        'title: Roles and permissions',
        'created in AWS',
        'RBAC',
        'product:',
        '- xl - deploy',
        '- xl - release',
        '- xl - platform',
        'category:',
        '- XL',
        'UP(BETA)',
        'subject:',
        '- Using',
        'XL',
        'UP',
        'tags:',
        '- xl',
        'up',
        '- Kubernetes',
        'order: 400',
        '---',
        '',
        'This page lists the RBAC service accounts with the roles and permissions created when ' +
        'deploying to the Kubernetes cluster.For more information, see[Adding an AWS user to a Kubernetes ' +
        'cluster\'s RBAC configuration](/xl-platform/how-to/create-an-aws-rbac-user.html), and ' +
        '[Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/).',
        'The service accounts are listed below:',
        '',
        '## Roles'
        '',
    ]
    markdown_lines.extend(extract_markdown(roles, role_bindings, 'Bound to role'))
    markdown_lines.append('## Cluster Roles')
    markdown_lines.append('')
    markdown_lines.extend(extract_markdown(cluster_roles, cluster_role_bindings, 'Bound to cluster role'))

    for markdown_line in markdown_lines:
        print(markdown_line)


if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
        print(f"Usage: python3 {os.path.basename(sys.argv[0])} > FILENAME.markdown")
        print('')
        print('Extracts all RBAC permissions and writes it to a markdown format compatible with the Docs team format.')
    else:
        main()
