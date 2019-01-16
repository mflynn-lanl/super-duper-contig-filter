/*
A KBase module: mcflynn_ContigFilter
This sample module contains one small method that filters contigs.
*/

module mcflynn_ContigFilter {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_mcflynn_ContigFilter(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

    funcdef run_mcflynn_ContigFilter_max(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
