
/* cdisort.i */

%module cdisort

%{
#include "cdisort.h"
#include "locate.h"
%}

/* Exclude standalone test functions from Python bindings */
%ignore print_test;
%ignore c_gaussian_quadrature_test;

%ignore disort_test01;
%ignore disort_test02;
%ignore disort_test03;
%ignore disort_test04;
%ignore disort_test05;
%ignore disort_test06;
%ignore disort_test07;
%ignore disort_test08;
%ignore disort_test09;
%ignore disort_test10;
%ignore disort_test11;
%ignore disort_test12;
%ignore disort_test13;
%ignore disort_test14;

/* Keep all numerical solver functions */
%include "cdisort.h"
%include "locate.h"
