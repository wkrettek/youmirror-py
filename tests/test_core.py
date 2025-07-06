"""
Gonna use this just to verify nothing breaks in the core (Or it does break on invalid input!)
"""
# TODO core does not work right now
# import youmirror.core as core
# import youmirror.configurer as configurer
# import youmirror.databaser as databaser
# from pathlib import Path
# import pytest
#
# # Create test config and db
# config = configurer.new_config(Path(configurer.config_file), '.')
# Path(databaser.db_file).touch()
#
# # Create a new YouMirror object
# ym = core.YouMirror(root='.')
#
# # Input some invalid urls to verify all our funcs that take them will return before it's too late
# def test_invalid_urls():
#     '''
#     Runs invalid urls through core functions that take them and verifies they return early
#     '''
#     # Invalid urls we wanna test against
#     invalid_urls = ["JUNK", "https://github.com", "https://www.youtube.com/watch?v=JUNK", "https://www.youtube.com/user/INVALID_USER", "https://www.youtube.com/channel/INVALID_CHANNEL", "https://www.youtube.com/c/INVALID_CHANNEL", "https://www.youtube.com/playlist?list=INVALID_PLAYLIST"]
#
#     funcs = [ym.add, ym.remove, ym.update, ym.sync] # All the functions we wanna test
#
#     # Run the functions on the invalid urls
#     for func in funcs:                              # For each function
#         for url in invalid_urls:                    # For each invalid url
#             assert func(url) == False               # Verify using the invalid url returns False
#
# # Just add and remove a single and verify there is no crash
# def test_add_sync_remove_single():
#     '''
#     Adds a single, syncs it, and removes it
#     '''
#     # Add a single
#     try:
#         # Force add for speed
#         ym.add("https://www.youtube.com/watch?v=6NQHtVrP3gE", **{"no_dl": True, "force": True})
#         ym.sync("https://www.youtube.com/watch?v=6NQHtVrP3gE")
#         ym.remove("https://www.youtube.com/watch?v=6NQHtVrP3gE", **{'no_rm': True, 'force': True})
#     except Exception as e:
#         pytest.fail("Failed due to %s", e)
#
# # Cleanup
# def test_cleanup():
#     '''
#     Cleanup
#     '''
#     Path(databaser.db_file).unlink()
#     Path(configurer.config_file).unlink()
