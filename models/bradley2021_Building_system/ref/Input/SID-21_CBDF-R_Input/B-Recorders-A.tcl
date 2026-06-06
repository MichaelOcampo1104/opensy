# ===================================================================================================================================================================================
# This script defines a set of recorders to produce desired output for various elements and nodes.
set recDrift [ recorder Drift -file "$out/Drift.txt" -time -iNode 39 44 49 39 55 60 65 55 -jNode 44 49 54 54 60 65 70 70 -dof 1 -perpDirn 2 ];# Drift.txt
set recNodalDisplacements [ recorder Node -file "$out/NodalDisplacements.txt" -time -dof 1 2 3 disp ];# NodalDisplacements.txt
set recNodalReactions [ recorder Node -file "$out/NodalReactions.txt" -time -dof 1 2 3 reaction ];# NodalReactions.txt
set recEle_529_Fiber_P23p0000 [ recorder Element -file "$out/Ele_529_Fiber_P23p0000.txt" -time -ele 529 section fiber +23.0000 0.0 stressStrain ];# Ele_529_Fiber_P23p0000.txt
set recEle_529_Fiber_P20p0000 [ recorder Element -file "$out/Ele_529_Fiber_P20p0000.txt" -time -ele 529 section fiber +20.0000 0.0 stressStrain ];# Ele_529_Fiber_P20p0000.txt
set recEle_529_Fiber_P17p0000 [ recorder Element -file "$out/Ele_529_Fiber_P17p0000.txt" -time -ele 529 section fiber +17.0000 0.0 stressStrain ];# Ele_529_Fiber_P17p0000.txt
set recEle_529_Fiber_P14p0000 [ recorder Element -file "$out/Ele_529_Fiber_P14p0000.txt" -time -ele 529 section fiber +14.0000 0.0 stressStrain ];# Ele_529_Fiber_P14p0000.txt
set recEle_529_Fiber_P6p0000 [ recorder Element -file "$out/Ele_529_Fiber_P6p0000.txt" -time -ele 529 section fiber +6.0000 0.0 stressStrain ];# Ele_529_Fiber_P6p0000.txt
set recEle_529_Fiber_P3p0000 [ recorder Element -file "$out/Ele_529_Fiber_P3p0000.txt" -time -ele 529 section fiber +3.0000 0.0 stressStrain ];# Ele_529_Fiber_P3p0000.txt
set recEle_529_Fiber_P0p0000 [ recorder Element -file "$out/Ele_529_Fiber_P0p0000.txt" -time -ele 529 section fiber +0.0000 0.0 stressStrain ];# Ele_529_Fiber_P0p0000.txt
set recEle_529_Fiber_N3p0000 [ recorder Element -file "$out/Ele_529_Fiber_N3p0000.txt" -time -ele 529 section fiber -3.0000 0.0 stressStrain ];# Ele_529_Fiber_N3p0000.txt
set recEle_529_Fiber_N10p5000 [ recorder Element -file "$out/Ele_529_Fiber_N10p5000.txt" -time -ele 529 section fiber -10.5000 0.0 stressStrain ];# Ele_529_Fiber_N10p5000.txt
set recEle_529_Fiber_P31p5000 [ recorder Element -file "$out/Ele_529_Fiber_P31p5000.txt" -time -ele 529 section fiber +31.5000 0.0 stressStrain ];# Ele_529_Fiber_P31p5000.txt
set recEle_577_Fiber_P6p0000 [ recorder Element -file "$out/Ele_577_Fiber_P6p0000.txt" -time -ele 577 section fiber +6.0000 0.0 stressStrain ];# Ele_577_Fiber_P6p0000.txt
set recEle_577_Fiber_P3p0000 [ recorder Element -file "$out/Ele_577_Fiber_P3p0000.txt" -time -ele 577 section fiber +3.0000 0.0 stressStrain ];# Ele_577_Fiber_P3p0000.txt
set recEle_577_Fiber_P0p0000 [ recorder Element -file "$out/Ele_577_Fiber_P0p0000.txt" -time -ele 577 section fiber +0.0000 0.0 stressStrain ];# Ele_577_Fiber_P0p0000.txt
set recEle_577_Fiber_N3p0000 [ recorder Element -file "$out/Ele_577_Fiber_N3p0000.txt" -time -ele 577 section fiber -3.0000 0.0 stressStrain ];# Ele_577_Fiber_N3p0000.txt
set recEle_577_Fiber_N6p0000 [ recorder Element -file "$out/Ele_577_Fiber_N6p0000.txt" -time -ele 577 section fiber -6.0000 0.0 stressStrain ];# Ele_577_Fiber_N6p0000.txt
set recEle_577_Fiber_P10p3000 [ recorder Element -file "$out/Ele_577_Fiber_P10p3000.txt" -time -ele 577 section fiber +10.3000 0.0 stressStrain ];# Ele_577_Fiber_P10p3000.txt
set recEle_577_Fiber_N10p3000 [ recorder Element -file "$out/Ele_577_Fiber_N10p3000.txt" -time -ele 577 section fiber -10.3000 0.0 stressStrain ];# Ele_577_Fiber_N10p3000.txt
set recEBCForces [ recorder Element -file "$out/EBCForces.txt" -time -ele \
   7   8   15  16  23  24  26  27  29  31  32  34  36  37  39  41  42  44  46  47  49  51  52  54  56  57  59  61  62  64  66  67  69  70  72  74  75  77  79  86  87  94  95  102 \
   109 110 117 118 125 132 133 140 141 148 149 151 152 154 156 157 159 161 162 164 165 167 169 170 172 174 181 182 189 190 197 204 205 212 213 220 221 223 224 226 228 229 231 233 \
   234 236 237 239 241 242 244 246 253 254 261 262 269 276 277 284 285 292 293 295 296 298 300 301 303 305 312 313 320 321 328 329 332 334 336 339 340 343 345 347 350 351 354 356 \
   358 361 362 365 367 369 372 373 376 378 380 383 384 387 389 391 394 395 398 400 402 405 406 409 411 413 416 417 420 422 424 427 428 431 433 435 438 439 442 444 446 449 450 453 \
   455 457 460 461 464 466 468 471 472 475 477 479 482 483 486 488 490 493 494 497 499 501 504 505 508 510 512 515 516 519 521 523 526 527 530 532 534 535 537 539 542 543 546 548 \
   550 551 553 555 558 559 562 564 566 567 569 571 574 575 578 580 582 585 586 589 591 593 596 597 600 602 604 607 608 611 613 615 618 619 622 624 626 629 630 633 635 637 640 641 \
   644 646 648 651 652 655 657 659 662 663 666 668 670 673 674 677 679 681 684 685 688 690 692 695 696 699 701 703 706 707 710 712 714 717 718 721 723 725 728 729 732 734 736 739 \
   740 743 745 747 750 751 754 756 758 761 762 765 767 769 772 773 776 778 780 783 784 787 789 791 794 795 798 800 802 805 806 809 811 813 816 817 820 822 824 827 828 831 833 835 \
   838 845 856 857 868 869 880 881 892 893 904 905 916 \
   force ];# EBCForces.txt
set recZLSForces [ recorder Element -file "$out/ZLSForces.txt" -time -ele \
   331 337 342 348 353 359 364 370 375 381 386 392 397 403 408 414 419 425 430 436 441 447 452 458 463 469 474 480 485 491 496 502 507 513 518 524 529 540 545 556 561 572 577 583 \
   588 594 599 605 610 616 621 627 632 638 643 649 654 660 665 671 676 682 687 693 698 704 709 715 720 726 731 737 742 748 753 759 764 770 775 781 786 792 797 803 808 814 819 825 \
   830 836 \
   force ];# ZLSForces.txt
set recZLSDeforms [ recorder Element -file "$out/ZLSDeforms.txt" -time -ele \
   331 337 342 348 353 359 364 370 375 381 386 392 397 403 408 414 419 425 430 436 441 447 452 458 463 469 474 480 485 491 496 502 507 513 518 524 529 540 545 556 561 572 577 583 \
   588 594 599 605 610 616 621 627 632 638 643 649 654 660 665 671 676 682 687 693 698 704 709 715 720 726 731 737 742 748 753 759 764 770 775 781 786 792 797 803 808 814 819 825 \
   830 836 \
   deformation ];# ZLSDeforms.txt
set recSpringForces [ recorder Element -file "$out/SpringForces.txt" -time -ele \
   25  28  30  33  35  38  40  43  45  48  50  53  55  58  60  63  65  68  71  73  76  78  150 153 155 158 160 163 166 168 171 173 222 225 227 230 232 235 238 240 243 245 294 297 \
   299 302 304 333 335 344 346 355 357 366 368 377 379 388 390 399 401 410 412 421 423 432 434 443 445 454 456 465 467 476 478 487 489 498 500 509 511 520 522 531 533 536 538 547 \
   549 552 554 563 565 568 570 579 581 590 592 601 603 612 614 623 625 634 636 645 647 656 658 667 669 678 680 689 691 700 702 711 713 722 724 733 735 744 746 755 757 766 768 777 \
   779 788 790 799 801 810 812 821 823 832 834 \
   force ];# SpringForces.txt
set recSpringDeforms [ recorder Element -file "$out/SpringDeforms.txt" -time -ele \
   25  28  30  33  35  38  40  43  45  48  50  53  55  58  60  63  65  68  71  73  76  78  150 153 155 158 160 163 166 168 171 173 222 225 227 230 232 235 238 240 243 245 294 297 \
   299 302 304 333 335 344 346 355 357 366 368 377 379 388 390 399 401 410 412 421 423 432 434 443 445 454 456 465 467 476 478 487 489 498 500 509 511 520 522 531 533 536 538 547 \
   549 552 554 563 565 568 570 579 581 590 592 601 603 612 614 623 625 634 636 645 647 656 658 667 669 678 680 689 691 700 702 711 713 722 724 733 735 744 746 755 757 766 768 777 \
   779 788 790 799 801 810 812 821 823 832 834 \
   deformation ];# SpringDeforms.txt
# ===================================================================================================================================================================================
