
import Debug exposing (log)
import Json.Decode exposing (field, int, string, list, Decoder)
import Json.Encode exposing (encode, object,string, int, Value)

import Html exposing (text, div, input, button, p, select,label,h1,h2,h3,h4,h5,h6,fieldset, Html)
import Html.Attributes exposing (value,multiple,style,placeholder,class)
import Html.Events exposing (onClick, onInput)
import Html exposing (program)
import Http exposing (get, post, request, jsonBody, Error, Response, Error(..), Body)
import Task  exposing (Task, succeed, fail, andThen, mapError)   

import Bootstrap.CDN as CDN
import Bootstrap.Form as Form
import Bootstrap.Form.Input as Input
import Bootstrap.Grid as Grid
import Bootstrap.Grid.Col as Col
import Bootstrap.Grid.Row as Row 
import Bootstrap.Button as Button

main =
  Html.program
    { init = init 
    , view = view
    , update = update
    , subscriptions = subscriptions
    }

subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none


-- MODEL
type alias User =
  { user_id: String
  , artists: List (Artist)
  , recommendation: List(Artist)
  }
  
type alias Artist =
  { id : String
  , full_name : String
  }

type alias Model =
  { user_id: String -- user_id under recommendation
  , artists: List (Artist)
  , recommendation: List(Artist)
  }

model : Model
model =
  { user_id=""
  , artists=[]
  , recommendation=[]
  }

init : (Model, Cmd Msg)
init =
  ( model, Cmd.none )

userDecoder : Decoder User
userDecoder =
    Json.Decode.map3 User
      (field "user_id" Json.Decode.string)
      (field "artists" listArtistsDecoder)
      (field "recommendation" listArtistsDecoder)

listArtistsDecoder: Decoder (List Artist)
listArtistsDecoder=
  Json.Decode.list artistDecoder

artistDecoder : Decoder Artist
artistDecoder =
    Json.Decode.map2 Artist
        (field "id"   Json.Decode.string)
        (field "full_name"  Json.Decode.string)

-- update

type Msg
  = Recommend
  | ChgUserId String
  | UserFound (Result Http.Error (User))
  


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    ChgUserId user_id ->
      ({model| user_id = user_id}, Cmd.none)

    Recommend ->
      (model, recommend model.user_id )
    
    UserFound (Ok user) ->
      ({model | artists=user.artists, recommendation=user.recommendation}, Cmd.none)


    UserFound (Err _) ->
      (model, Cmd.none)

recommend : String -> Cmd Msg
recommend user_id=
  let
    json =Http.jsonBody <|
      object
      [ ("user_id", (Json.Encode.string user_id))]
  in      
    sendPost UserFound ("http://localhost:8887/recommendation") userDecoder json

sendGet : (Result Error a -> msg) -> String -> Decoder a -> Cmd msg
sendGet msg url decoder =
  Http.get url decoder |> Http.send msg

sendPost : (Result Error a -> msg) -> String -> Decoder a -> Body -> Cmd msg
sendPost msg url decoder body2 =
    Http.post url body2 decoder |> Http.send msg
    
-- VIEW
viewAllArtists: Model -> List (Html Msg)
viewAllArtists model=
    [ div []
      [ h6 [] [text "Artists"]
      , Grid.container []
                (List.map (\artist -> 
                    Grid.row []
                      [ Grid.col [] 
                          [ label [] [ text artist.full_name ]]
                      ]
                ) model.artists)
      ]
  ]

viewRecommendation: Model -> List (Html Msg) 
viewRecommendation model=
    [ div []
      [ h6 [] [text "Recommendation"]
      , Grid.container []
                ( List.map (\artist ->
                    Grid.row []
                      [ Grid.col []
                        [ label [] [text artist.full_name]]
                      ]
                ) model.recommendation)
      ]
    ]


view : Model -> Html Msg
view model =
  div []
  [ Grid.container []
    [ CDN.stylesheet -- creates an inline style node with the Bootstrap CSS
    , Grid.row []
        [ Grid.col [] 
          [ Form.formInline [] 
            [ Input.text [ Input.attrs [placeholder "User ID"], Input.onInput ChgUserId]  
            , Button.button [Button.primary, Button.onClick Recommend, Button.attrs [ class "ml-sm-2 my-2" ] ] [ text "Go" ] 
            ]
          ]
        ]
    , Grid.row []
        [ Grid.col [Col.xs6 ]
          (viewAllArtists model)  

        , Grid.col [ Col.xs6]
          (viewRecommendation model)
        ]
    ]
  ]