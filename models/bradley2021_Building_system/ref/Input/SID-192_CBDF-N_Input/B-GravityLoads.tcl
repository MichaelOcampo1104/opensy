# ==========================================================================================
# This script defines the gravity load pattern for the building system. The gravity load
# patterin is comprised of point loads applied to column nodes at floor levels, which
# represent out-of-plane framing loads, and distributed loads applied to the beam elements,
# which represent tributary floor and roof loads of the beams.


pattern Plain 1 Linear {                                                                 
# ------------------------------------------------------------------------------------------
# Concentrated loads applied to column nodes at floor levels
# ------------------------------------------------------------------------------------------
load    8     +0.000000e+00 -4.279000e+01 +0.000000e+00                        ;# C1
load    16    +0.000000e+00 -4.279000e+01 +0.000000e+00                        ;# C2
load    24    +0.000000e+00 -2.230500e+01 +0.000000e+00                        ;# C3
load    28    +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C4
load    33    +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C5
load    38    +0.000000e+00 -2.520000e+01 +0.000000e+00                        ;# C6
load    44    +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C7
load    49    +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C8
load    54    +0.000000e+00 -2.520000e+01 +0.000000e+00                        ;# C9
load    60    +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C10
load    65    +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C11
load    70    +0.000000e+00 -2.520000e+01 +0.000000e+00                        ;# C12
load    74    +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C13
load    79    +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C14
load    84    +0.000000e+00 -2.520000e+01 +0.000000e+00                        ;# C15
load    92    +0.000000e+00 -4.279000e+01 +0.000000e+00                        ;# C16
load    100   +0.000000e+00 -4.279000e+01 +0.000000e+00                        ;# C17
load    108   +0.000000e+00 -2.230500e+01 +0.000000e+00                        ;# C18
load    116   +0.000000e+00 -4.279000e+01 +0.000000e+00                        ;# C19
load    124   +0.000000e+00 -4.279000e+01 +0.000000e+00                        ;# C20
load    132   +0.000000e+00 -2.230500e+01 +0.000000e+00                        ;# C21
load    140   +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C22
load    148   +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C23
load    156   +0.000000e+00 -2.520000e+01 +0.000000e+00                        ;# C24
load    160   +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C25
load    165   +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C26
load    170   +0.000000e+00 -2.520000e+01 +0.000000e+00                        ;# C27
load    174   +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C28
load    179   +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C29
load    184   +0.000000e+00 -2.520000e+01 +0.000000e+00                        ;# C30
load    192   +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C31
load    200   +0.000000e+00 -5.810000e+01 +0.000000e+00                        ;# C32
load    208   +0.000000e+00 -2.520000e+01 +0.000000e+00                        ;# C33
load    216   +0.000000e+00 -4.279000e+01 +0.000000e+00                        ;# C34
load    224   +0.000000e+00 -4.279000e+01 +0.000000e+00                        ;# C35
load    232   +0.000000e+00 -2.230500e+01 +0.000000e+00                        ;# C36
load    236   +0.000000e+00 -2.185300e+01 +0.000000e+00                        ;# C37
load    241   +0.000000e+00 -2.185300e+01 +0.000000e+00                        ;# C38
load    246   +0.000000e+00 -1.147600e+01 +0.000000e+00                        ;# C39
load    250   +0.000000e+00 -2.905000e+01 +0.000000e+00                        ;# C40
load    255   +0.000000e+00 -2.905000e+01 +0.000000e+00                        ;# C41
load    260   +0.000000e+00 -1.260000e+01 +0.000000e+00                        ;# C42
load    268   +0.000000e+00 -2.905000e+01 +0.000000e+00                        ;# C43
load    276   +0.000000e+00 -2.905000e+01 +0.000000e+00                        ;# C44
load    284   +0.000000e+00 -1.260000e+01 +0.000000e+00                        ;# C45
load    292   +0.000000e+00 -2.905000e+01 +0.000000e+00                        ;# C46
load    300   +0.000000e+00 -2.905000e+01 +0.000000e+00                        ;# C47
load    308   +0.000000e+00 -1.260000e+01 +0.000000e+00                        ;# C48
load    312   +0.000000e+00 -2.905000e+01 +0.000000e+00                        ;# C49
load    317   +0.000000e+00 -2.905000e+01 +0.000000e+00                        ;# C50
load    322   +0.000000e+00 -1.260000e+01 +0.000000e+00                        ;# C51
load    330   +0.000000e+00 -2.185300e+01 +0.000000e+00                        ;# C52
load    338   +0.000000e+00 -2.185300e+01 +0.000000e+00                        ;# C53
load    346   +0.000000e+00 -1.147600e+01 +0.000000e+00                        ;# C54

# ------------------------------------------------------------------------------------------
# Uniform distributed loads applied to beam elements
# ------------------------------------------------------------------------------------------
eleLoad -ele  329 332 334 336 339             -type -beamUniform -6.916667e-02 ;# B1
eleLoad -ele  340 343 345 347 350             -type -beamUniform -6.916667e-02 ;# B2
eleLoad -ele  351 354 356 358 361             -type -beamUniform -3.000000e-02 ;# B3
eleLoad -ele  362 365 367 369 372             -type -beamUniform -6.916667e-02 ;# B4
eleLoad -ele  373 376 378 380 383             -type -beamUniform -6.916667e-02 ;# B5
eleLoad -ele  384 387 389 391 394             -type -beamUniform -3.000000e-02 ;# B6
eleLoad -ele  395 398 400 402 405             -type -beamUniform -6.916667e-02 ;# B7
eleLoad -ele  406 409 411 413 416             -type -beamUniform -6.916667e-02 ;# B8
eleLoad -ele  417 420 422 424 427             -type -beamUniform -3.000000e-02 ;# B9
eleLoad -ele  428 431 433 435 438             -type -beamUniform -6.916667e-02 ;# B10
eleLoad -ele  439 442 444 446 449             -type -beamUniform -6.916667e-02 ;# B11
eleLoad -ele  450 453 455 457 460             -type -beamUniform -3.000000e-02 ;# B12
eleLoad -ele  461 464 466 468 471             -type -beamUniform -6.916667e-02 ;# B13
eleLoad -ele  472 475 477 479 482             -type -beamUniform -6.916667e-02 ;# B14
eleLoad -ele  483 486 488 490 493             -type -beamUniform -3.000000e-02 ;# B15
eleLoad -ele  494 497 499 501 504             -type -beamUniform -6.916667e-02 ;# B16
eleLoad -ele  505 508 510 512 515             -type -beamUniform -6.916667e-02 ;# B17
eleLoad -ele  516 519 521 523 526             -type -beamUniform -3.000000e-02 ;# B18
eleLoad -ele  527 530 532 534 535 537 539 542 -type -beamUniform -6.916667e-02 ;# B19
eleLoad -ele  543 546 548 550 551 553 555 558 -type -beamUniform -6.916667e-02 ;# B20
eleLoad -ele  559 562 564 566 567 569 571 574 -type -beamUniform -3.000000e-02 ;# B21
eleLoad -ele  575 578 580 582 585             -type -beamUniform -6.916667e-02 ;# B22
eleLoad -ele  586 589 591 593 596             -type -beamUniform -6.916667e-02 ;# B23
eleLoad -ele  597 600 602 604 607             -type -beamUniform -3.000000e-02 ;# B24
eleLoad -ele  608 611 613 615 618             -type -beamUniform -6.916667e-02 ;# B25
eleLoad -ele  619 622 624 626 629             -type -beamUniform -6.916667e-02 ;# B26
eleLoad -ele  630 633 635 637 640             -type -beamUniform -3.000000e-02 ;# B27
eleLoad -ele  641 644 646 648 651             -type -beamUniform -6.916667e-02 ;# B28
eleLoad -ele  652 655 657 659 662             -type -beamUniform -6.916667e-02 ;# B29
eleLoad -ele  663 666 668 670 673             -type -beamUniform -3.000000e-02 ;# B30
eleLoad -ele  674 677 679 681 684             -type -beamUniform -7.275000e-02 ;# B31
eleLoad -ele  685 688 690 692 695             -type -beamUniform -7.275000e-02 ;# B32
eleLoad -ele  696 699 701 703 706             -type -beamUniform -4.195833e-02 ;# B33
eleLoad -ele  707 710 712 714 717             -type -beamUniform -7.275000e-02 ;# B34
eleLoad -ele  718 721 723 725 728             -type -beamUniform -7.275000e-02 ;# B35
eleLoad -ele  729 732 734 736 739             -type -beamUniform -4.195833e-02 ;# B36
eleLoad -ele  740 743 745 747 750             -type -beamUniform -7.275000e-02 ;# B37
eleLoad -ele  751 754 756 758 761             -type -beamUniform -7.275000e-02 ;# B38
eleLoad -ele  762 765 767 769 772             -type -beamUniform -4.195833e-02 ;# B39
eleLoad -ele  773 776 778 780 783             -type -beamUniform -7.275000e-02 ;# B40
eleLoad -ele  784 787 789 791 794             -type -beamUniform -7.275000e-02 ;# B41
eleLoad -ele  795 798 800 802 805             -type -beamUniform -4.195833e-02 ;# B42
eleLoad -ele  806 809 811 813 816             -type -beamUniform -7.275000e-02 ;# B43
eleLoad -ele  817 820 822 824 827             -type -beamUniform -7.275000e-02 ;# B44
eleLoad -ele  828 831 833 835 838             -type -beamUniform -4.195833e-02 ;# B45
}                                                                                        
# ==========================================================================================
