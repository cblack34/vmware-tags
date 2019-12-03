import getpass
import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
import urllib3
from requests.exceptions import SSLError, HTTPError
from vmwareRest.vmwareRest import vmwareRest

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_parser():
    parser = ArgumentParser(description="""
    A utility for to retrieve computers based on tags.
    """)
    # task_group = parser.add_mutually_exclusive_group(required=True)
    # task_group.add_argument("--deploy", "-d", help="Run Deploy task on agent", action='store_true')
    # task_group.add_argument("--scan", "-s", help="Run Scan task on agent", action='store_true')
    # task_group.add_argument("--task", "-t", help="Run this task")
    # task_group.add_argument("--checkin", "-c", help="Run agent checkin", action='store_true')

    parser.add_argument("--url", help="Server URL without a trailing 'https://<server>[:port].", required=True)
    parser.add_argument("--insecure", help="Don't validate Server SSL cert.", action='store_false')
    parser.add_argument("--user", "-u", help="Username to use on server: <user>@<domain>", required=True)
    parser.add_argument("--password", "-p", help="Password to use on Server")
    parser.add_argument("--output", "-o", help="Directory to create files")

    parser.add_argument("--force", help="Force overwriting of files in output directory.", action='store_true')

    return parser


def main():
    args = create_parser().parse_args()

    password = args.password
    if args.user is not None and args.password is None:
        password = getpass.getpass(prompt='Password: ', stream=None)

    try:
        vmware = vmwareRest(args.url, args.user, password, args.insecure)
        all_cats = vmware.get_tags_categories().json()['value']

    except SSLError as e:
        print(f"SSL Error on: {args.url}\nPlease check the cert or use the --insecure flag.")
        sys.exit()

    except HTTPError as e:
        print(e)
        # print(f"Bad username or password for {args.url}")
        sys.exit()

    try:
        vm_cats = [i for i in all_cats if 'VirtualMachine' in vmware.get_tag_category_info(i).json().get('value').get('associable_types')]

    except Exception as e:
        pprint(e)

    print(f"\n\n\n\n{'Index':>5} :: Category Name")
    for i, cat in enumerate(vm_cats):
        cat_info = vmware.get_tag_category_info(cat).json()
        print(f"{i:>5} :: {cat_info['value']['name']}")

    print("\n\n")

    all_tags = vmware.get_tags().json()['value']

    # filtered_tags = [tag for tag in all_tags if vmware.get_tag_info(tag).json()['value']['category_id'] == vm_cats[3]]
    #
    # for tag in filtered_tags:
    #     print(vmware.get_tag_info(tag).json()['value']['name'])

    while True:
        try:
            user_choice = int(input("Please enter the index of the category you want to retrieve: "))
            if user_choice < len(vm_cats):
                break
            else:
                print(f"{user_choice} is not a valid index.")

        except ValueError as e:
            print("input must be an integer.")

    # filtered_tags = [k for k, v in all_tags.items() if v['category_id'] == vm_cats[user_choice]]
    filtered_tags = [tag for tag in all_tags if vmware.get_tag_info(tag).json()['value']['category_id'] == vm_cats[user_choice]]

    # for k, v in all_tags.items():
    #     pprint(v)
    #     if v['category_id'] == vm_cats[user_choice]:
    #         pprint(v)

    if args.output:
        if args.output == '.':
            output_dir = Path()
        else:
            output_dir = Path(args.output)

        if args.force:
            open_mode = 'w'
        else:
            open_mode = 'x'

        if not output_dir.exists():
            print(f"Output directory does not exist.\n{args.output}")
            sys.exit()

        for tag in filtered_tags:
            try:
                output_file_name = vmware.get_tag_info(tag).json()['value']['name'] + ".txt"
                with open(output_dir / output_file_name, open_mode) as f:
                    [f.write(vmware.get_vm(i['id']).get('name') + '\n') for i in vmware.get_vms_by_tags(tag)]
            except FileExistsError as e:
                print(f"{output_dir/output_file_name} already exist. Use --force if you would like to overwrite it.")

    else:
        for tag in filtered_tags:
            print(f"## {vmware.get_tag_info(tag).json()['value']['name']}\n")
            [print(vmware.get_vm(i['id']).get('name')) for i in vmware.get_vms_by_tags(tag)]
