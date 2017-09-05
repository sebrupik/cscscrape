#!/usr/bin/env python3

import re
import requests



def get_div_block(html_file, div_class):
    div_block = ""
    div_count = 0
    match = False
    for line in html_file.splitlines():
        #print(line)
        if re.search(div_class, line):
            match = True
            #print("found a match {0}".format(line))

        if match:
            if re.search("<div.*", line):
                div_count += 1

            if div_count > 0:
                div_block += line+"\n"

            if re.search("</div.*", line):
                div_count -= 1

            if div_count is 0:
                break;

    return div_block


def get_value(div_block):
    for index, value in enumerate(div_block.splitlines()):
        if index == 1:
            return value.strip()



def print_profile_attr(html_file):


    print("User name {0}".format("unknown"))
    block0 = get_div_block(html_file, "lia-component-users-widget-profile-user-name")
    print("User name: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-user-name-link"), "lia-statistic-value"))))

    block0 = get_div_block(html_file, "lia-component-user-rank")
    print("Rank: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-component-user-rank"), "lia-component-user-rank"))))

    block0 = get_div_block(html_file, "lia-component-quilt-user-profile-statistics")
    print("Overall posts: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-statistic-net_overall_posts"), "lia-statistic-value"))))
    print("kudos: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-statistic-net_kudos_weight_received"), "lia-statistic-value"))))
    print("solutions: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-statistic-net_accepted_solutions"), "lia-statistic-value"))))


def main():
   r = requests.get("https://supportforums.cisco.com/t5/cisco-support-community/ct-p/5411-support-community-home")
   print(get_div_block(r.text, "lia-vitality-metrics-display-completed-registrations"))


   r = requests.get("https://supportforums.cisco.com/t5/user/viewprofilepage/user-id/324976")
   print_profile_attr(r.text)
   #block0 = get_div_block(r.text, "lia-component-quilt-user-profile-statistics")

   #print(get_div_block(get_div_block(block0, "lia-statistic-net_overall_posts"), "lia-statistic-value"))
   #print(get_div_block(get_div_block(block0, "lia-statistic-net_kudos_weight_received"), "lia-statistic-value"))
   #print(get_div_block(get_div_block(block0, "lia-statistic-net_accepted_solutions"), "lia-statistic-value"))

if __name__ == "__main__":
    main()
