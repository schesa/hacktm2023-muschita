import sherlock

def find_social_media_profiles(username):
    results = sherlock.sherlock(username)
    return results

# Main program
if __name__ == "__main__":
    # Set the username for which you want to find social media profiles
    username = "mihaisimi"

    # Find social media profiles
    profiles = find_social_media_profiles(username)

    # Print the identified profiles
    if profiles:
        print("Social media profiles found:")
        for profile in profiles:
            print(profile)
    else:
        print("No social media profiles found.")
