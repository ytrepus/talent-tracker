from modules.seed import commit_data, clear_old_data


def main():
    clear_old_data()
    commit_data()


if __name__ == '__main__':
    main()
