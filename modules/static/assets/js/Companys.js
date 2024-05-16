class Company {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            init: true,
            companyTable: {
                initialize: false,
                id: null,
                ajax: {
                    url: "/get_companys/",
                    dataSrc: "data",
                },
            },
            list: {
                id: 'select[name"company_id"]',
                ajax: {
                    url: function () {
                        return "/get_users_with_access/";
                    },
                },
            },
        };

        self.data = defaultOptions.data;

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get_users_with_access/",
                    data: {
                        isList: true,
                    },
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
                        $.each(response["data"], function (index, value) {
                            select.append(
                                `<option value="${value["id"]}">
                                ${value["name"]}
                            </option>`
                            );
                        });
                    },
                    error: function (xhr, status, error) {},
                });
            };
        }

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };
        }

        self.init();
    }

    init() {
        const self = this;

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
    }
}
