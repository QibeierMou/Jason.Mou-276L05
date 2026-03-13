*** Settings ***
Documentation     Acceptance tests for the Shopping Basket API
...               Run with: robot features/basket.robot
Library           RequestsLibrary
Library           Collections

Suite Setup       Create Session    basket_api    http://localhost:5001

*** Variables ***
${BASE_URL}       http://localhost:5001

*** Test Cases ***
# ─── AC-001: Add a book to basket ─────────────────────────────────────────────
Add Valid Book To Basket
    [Documentation]    AC-001: A book in stock is added to the basket
    [Setup]    Clear Basket
    Given the basket is empty
    When the customer adds book    BK001    qty=1
    Then the basket contains    1    item
    And the basket total is greater than    0

# ─── AC-002: Cannot add out-of-stock book ──────────────────────────────────
Cannot Add Out Of Stock Book
    [Documentation]    AC-002: Out-of-stock books cannot be added
    [Setup]    Clear Basket
    When the customer tries to add book    BK003    qty=1
    Then the response status should be    409

# ─── AC-003: Remove a book from basket ───────────────────────────────────────
Remove Book From Basket
    [Documentation]    AC-003: A book in the basket can be removed
    [Setup]    Clear Basket
    Given the customer adds book    BK001    qty=1
    When the customer removes book    BK001
    Then the basket contains    0    items

# ─── AC-004: Apply valid discount code ────────────────────────────────────────
Apply Valid Discount Code
    [Documentation]    AC-004: SAVE10 reduces total by 10%
    [Setup]    Clear Basket
    Given the customer adds book    BK001    qty=1
    When the customer applies discount code    SAVE10
    Then the basket total includes a 10 percent discount

# ─── AC-005: Invalid discount code rejected ────────────────────────────────
Invalid Discount Code Is Rejected
    [Documentation]    AC-005: Unrecognised codes return an error
    [Setup]    Clear Basket
    When the customer tries to apply discount code    BOGUS99
    Then the response status should be    400

*** Keywords ***

Clear Basket
    ${resp}=    DELETE    ${BASE_URL}/basket/clear
    Should Be Equal As Integers    ${resp.status_code}    200

The basket is empty
    ${resp}=    GET    ${BASE_URL}/basket
    Should Be Equal    ${resp.json()}[items]    ${{{}}}

The customer adds book
    [Arguments]    ${book_id}    ${qty}=1
    ${qty_int}=    Convert To Integer    ${qty}
    ${body}=    Create Dictionary    book_id=${book_id}    qty=${qty_int}
    ${resp}=    POST    ${BASE_URL}/basket/item    json=${body}    expected_status=201
    Set Suite Variable    ${LAST_RESPONSE}    ${resp}

The customer tries to add book
    [Arguments]    ${book_id}    ${qty}=1
    ${qty_int}=    Convert To Integer    ${qty}
    ${body}=    Create Dictionary    book_id=${book_id}    qty=${qty_int}
    ${resp}=    POST    ${BASE_URL}/basket/item    json=${body}    expected_status=any
    Set Suite Variable    ${LAST_RESPONSE}    ${resp}

The basket contains
    [Arguments]    ${count}    ${unit}
    ${resp}=    GET    ${BASE_URL}/basket
    Length Should Be    ${resp.json()}[items]    ${count}

The basket total is greater than
    [Arguments]    ${amount}
    ${resp}=    GET    ${BASE_URL}/basket
    Should Be True    ${resp.json()}[total] > ${amount}

The response status should be
    [Arguments]    ${expected_status}
    Should Be Equal As Integers    ${LAST_RESPONSE.status_code}    ${expected_status}

The customer removes book
    [Arguments]    ${book_id}
    ${resp}=    DELETE    ${BASE_URL}/basket/item/${book_id}    expected_status=200
    Set Suite Variable    ${LAST_RESPONSE}    ${resp}

The customer applies discount code
    [Arguments]    ${code}
    ${body}=    Create Dictionary    code=${code}
    ${resp}=    POST    ${BASE_URL}/basket/discount    json=${body}    expected_status=200
    Set Suite Variable    ${LAST_RESPONSE}    ${resp}

The customer tries to apply discount code
    [Arguments]    ${code}
    ${body}=    Create Dictionary    code=${code}
    ${resp}=    POST    ${BASE_URL}/basket/discount    json=${body}    expected_status=any
    Set Suite Variable    ${LAST_RESPONSE}    ${resp}

The basket total includes a 10 percent discount
    ${resp}=    GET    ${BASE_URL}/basket
    ${subtotal}=    Set Variable    ${resp.json()}[subtotal]
    ${total}=    Set Variable    ${resp.json()}[total]
    ${expected}=    Evaluate    round(${subtotal} * 0.9, 2)
    Should Be Equal As Numbers    ${total}    ${expected}